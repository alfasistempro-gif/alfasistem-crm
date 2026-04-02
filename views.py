from decimal import Decimal, InvalidOperation

from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.utils import timezone
from accounting.models import Account, JournalEntry, JournalEntryLine, AccountReceivable

from .models import (
    Sale,
    SaleItem,
    Payment,
    SavedOrder,
    SavedOrderItem,
    CashOpening,
    CashClosing,
    CashClosingDenomination,
    CashRemittance,
    CashRemittanceDenomination,
)
from customers.models import Customer
from catalog.models import Product
from inventory_pt.models import FinishedProductInventory


POS_SESSION_KEY = 'billing_pos_draft_v24'
POS_CASH_SESSION_KEY = 'billing_pos_cash_session_v27'
POS_HOLD_SLOTS_KEY = 'billing_pos_hold_slots_v210'


def _safe_decimal(value, default='0.00'):
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return Decimal(default)


def _empty_pos_draft():
    return {
        'mode': 'customer',
        'customer_id': None,
        'customer_name': '',
        'items': [],
        'total_items': 0,
        'total_amount': '0.00',
        'document_type': '',
        'status': 'draft',
    }


def _empty_cash_session():
    return {
        'is_open': False,
        'station_name': 'caja actual 1',
        'sales_channel': 'canal de ventas 1',
        'cashier_name': 'alfasistem',
        'opening_amount': '0.00',
        'current_ticket_number': '',
    }


def _empty_hold_slots():
    return {
        'station_name': 'caja actual 1',
        'slot_1': None,
        'slot_2': None,
        'slot_3': None,
    }


def _recalculate_pos_draft(draft):
    total_items = 0
    total_amount = Decimal('0.00')

    for item in draft.get('items', []):
        quantity = int(item.get('quantity', 0) or 0)
        price = _safe_decimal(item.get('price', '0.00'))
        discount = _safe_decimal(item.get('discount', '0.00'))

        subtotal = (price * quantity) - discount
        if subtotal < 0:
            subtotal = Decimal('0.00')

        item['quantity'] = quantity
        item['price'] = f"{price:.2f}"
        item['discount'] = f"{discount:.2f}"
        item['subtotal'] = f"{subtotal:.2f}"

        total_items += quantity
        total_amount += subtotal

    draft['total_items'] = total_items
    draft['total_amount'] = f"{total_amount:.2f}"
    return draft


def _get_pos_draft(request):
    draft = request.session.get(POS_SESSION_KEY)

    if not draft:
        draft = _empty_pos_draft()

    return _recalculate_pos_draft(draft)


def _save_pos_draft(request, draft):
    request.session[POS_SESSION_KEY] = _recalculate_pos_draft(draft)
    request.session.modified = True


def _get_cash_session(request):
    cash_session = request.session.get(POS_CASH_SESSION_KEY)

    if not cash_session:
        cash_session = _empty_cash_session()

    return cash_session


def _save_cash_session(request, cash_session):
    request.session[POS_CASH_SESSION_KEY] = cash_session
    request.session.modified = True


def _get_hold_slots(request):
    hold_slots = request.session.get(POS_HOLD_SLOTS_KEY)

    if not hold_slots:
        hold_slots = _empty_hold_slots()

    return hold_slots


def _save_hold_slots(request, hold_slots):
    request.session[POS_HOLD_SLOTS_KEY] = hold_slots
    request.session.modified = True


def sale_home(request):
    draft = _get_pos_draft(request)
    cash_session = _get_cash_session(request)
    hold_slots = _get_hold_slots(request)

    context = {
        'pos_draft': draft,
        'selected_mode': draft.get('mode', 'customer'),
        'selected_customer_name': draft.get('customer_name', ''),
        'cash_session': cash_session,
        'hold_slots': hold_slots,
    }
    return render(request, 'billing/sale_home.html', context)


@require_POST
def pos_set_mode(request):
    mode = request.POST.get('mode', 'customer').strip().lower()
    draft = _get_pos_draft(request)

    if mode not in ['customer', 'varios']:
        return JsonResponse({
            'success': False,
            'message': 'Modo inválido.',
        }, status=400)

    draft['mode'] = mode

    if mode == 'varios':
        draft['customer_id'] = None
        draft['customer_name'] = 'Clientes varios'

    if mode == 'customer' and draft.get('customer_name') == 'Clientes varios':
        draft['customer_id'] = None
        draft['customer_name'] = ''

    _save_pos_draft(request, draft)

    return JsonResponse({
        'success': True,
        'mode': draft['mode'],
        'customer_name': draft['customer_name'],
        'total_items': draft['total_items'],
        'total_amount': draft['total_amount'],
    })


@require_POST
def pos_set_document_type(request):
    document_type = request.POST.get('document_type', '').strip().lower()
    draft = _get_pos_draft(request)

    if document_type not in ['ticket', 'ccf']:
        return JsonResponse({
            'success': False,
            'message': 'Tipo de documento inválido.',
        }, status=400)

    draft['document_type'] = document_type
    _save_pos_draft(request, draft)

    return JsonResponse({
        'success': True,
        'document_type': draft['document_type'],
    })


@require_POST
def pos_open_cash_register(request):
    password = request.POST.get('password', '').strip()
    opening_amount = _safe_decimal(request.POST.get('opening_amount', '0.00'))

    cash_session = _get_cash_session(request)

    active_opening = CashOpening.objects.filter(
        station_name='caja actual 1',
        closed_at__isnull=True,
    ).order_by('-opened_at').first()

    if active_opening:
        cash_session['is_open'] = True
        cash_session['current_ticket_number'] = cash_session.get('current_ticket_number', '') or 'T-000001'
        _save_cash_session(request, cash_session)

        return JsonResponse({
            'success': False,
            'message': 'La caja ya está abierta.',
        }, status=400)

    cash_session['is_open'] = False
    cash_session['current_ticket_number'] = ''
    _save_cash_session(request, cash_session)

    if not password:
        return JsonResponse({
            'success': False,
            'message': 'La contraseña es obligatoria.',
        }, status=400)

    if opening_amount < Decimal('5.00'):
        return JsonResponse({
            'success': False,
            'message': 'La apertura no puede ser menor a $5.00.',
        }, status=400)

    opening = CashOpening.objects.create(
        station_name='caja actual 1',
        sales_channel='canal de ventas 1',
        cashier_name='alfasistem',
        opening_password_snapshot=password,
        opening_amount=opening_amount,
        opened_at=timezone.now(),
    )

    cash_session['is_open'] = True
    cash_session['current_ticket_number'] = 'T-000001'
    cash_session['opened_at'] = opening.opened_at.strftime('%Y-%m-%d %H:%M:%S')
    cash_session['opening_amount'] = f'{float(opening.opening_amount):.2f}'
    _save_cash_session(request, cash_session)

    return JsonResponse({
        'success': True,
        'message': 'Caja abierta correctamente.',
        'cash_state': 'open',
        'button_label': 'Caja abierta',
        'current_ticket_number': 'T-000001',
        'opened_at': opening.opened_at.strftime('%Y-%m-%d %H:%M:%S'),
        'opening_amount': f'{float(opening.opening_amount):.2f}',
        'cash_opening_id': opening.id,
    })


@require_POST
def pos_close_cash_session(request):
    cash_session = _get_cash_session(request)

    cash_session['is_open'] = False
    cash_session['current_ticket_number'] = ''

    _save_cash_session(request, cash_session)

    return JsonResponse({
        'success': True,
        'message': 'Caja cerrada correctamente.',
        'cash_state': 'closed',
        'button_label': 'Abrir caja',
        'current_ticket_number': '',
    })
def _cash_denominations():
    return [
        Decimal('100.00'),
        Decimal('50.00'),
        Decimal('20.00'),
        Decimal('10.00'),
        Decimal('5.00'),
        Decimal('1.00'),
        Decimal('0.25'),
        Decimal('0.10'),
        Decimal('0.05'),
        Decimal('0.01'),
    ]

@require_POST
def pos_open_cash_register(request):
    password = request.POST.get('password', '').strip()
    opening_amount = _safe_decimal(request.POST.get('opening_amount', '0.00'))

    cashier_name = (
        request.user.username
        if getattr(request, 'user', None) and request.user.is_authenticated
        else 'alfasistem'
    )

    cash_session = _get_cash_session(request)

    active_opening = CashOpening.objects.filter(
        station_name='caja actual 1',
        is_active=True,
    ).order_by('-opened_at').first()

    if active_opening:
        cash_session['is_open'] = True
        cash_session['current_ticket_number'] = cash_session.get('current_ticket_number', '') or 'T-000001'
        cash_session['opened_at'] = active_opening.opened_at.strftime('%Y-%m-%d %H:%M:%S')
        cash_session['opening_amount'] = f'{float(active_opening.opening_amount):.2f}'
        _save_cash_session(request, cash_session)

        return JsonResponse({
            'success': False,
            'message': 'La caja ya está abierta.',
        }, status=400)

    cash_session['is_open'] = False
    cash_session['current_ticket_number'] = ''
    cash_session['opened_at'] = ''
    cash_session['opening_amount'] = '0.00'
    _save_cash_session(request, cash_session)

    if not password:
        return JsonResponse({
            'success': False,
            'message': 'La contraseña es obligatoria.',
        }, status=400)

    if opening_amount < Decimal('5.00'):
        return JsonResponse({
            'success': False,
            'message': 'La apertura no puede ser menor a $5.00.',
        }, status=400)

    opening = CashOpening.objects.create(
        station_name='caja actual 1',
        sales_channel='canal de ventas 1',
        cashier_name=cashier_name,
        opening_password_snapshot=password,
        opening_amount=opening_amount,
        is_active=True,
        opened_at=timezone.now(),
    )

    cash_session['is_open'] = True
    cash_session['current_ticket_number'] = 'T-000001'
    cash_session['opened_at'] = opening.opened_at.strftime('%Y-%m-%d %H:%M:%S')
    cash_session['opening_amount'] = f'{float(opening.opening_amount):.2f}'
    _save_cash_session(request, cash_session)

    return JsonResponse({
        'success': True,
        'message': 'Caja abierta correctamente.',
        'cash_state': 'open',
        'button_label': 'Caja abierta',
        'current_ticket_number': 'T-000001',
        'opened_at': opening.opened_at.strftime('%Y-%m-%d %H:%M:%S'),
        'opening_amount': f'{float(opening.opening_amount):.2f}',
        'cash_opening_id': opening.id,
    })


@require_POST
def pos_close_cash_session(request):
    active_opening = CashOpening.objects.filter(
        station_name='caja actual 1',
        is_active=True,
    ).order_by('-opened_at').first()

    cash_session = _get_cash_session(request)

    if active_opening:
        cash_session['is_open'] = True
        cash_session['current_ticket_number'] = cash_session.get('current_ticket_number', '') or 'T-000001'
        cash_session['opened_at'] = active_opening.opened_at.strftime('%Y-%m-%d %H:%M:%S')
        cash_session['opening_amount'] = f'{float(active_opening.opening_amount):.2f}'
    else:
        cash_session['is_open'] = False
        cash_session['current_ticket_number'] = ''
        cash_session['opened_at'] = ''
        cash_session['opening_amount'] = '0.00'

    _save_cash_session(request, cash_session)

    return JsonResponse({
        'success': True,
        'cash_state': 'open' if active_opening else 'closed',
        'button_label': 'Caja abierta' if active_opening else 'Abrir caja',
        'current_ticket_number': cash_session.get('current_ticket_number', ''),
    })


def _cash_denominations():
    return [
        Decimal('100.00'),
        Decimal('50.00'),
        Decimal('20.00'),
        Decimal('10.00'),
        Decimal('5.00'),
        Decimal('1.00'),
        Decimal('0.25'),
        Decimal('0.10'),
        Decimal('0.05'),
        Decimal('0.01'),
    ]


def pos_search_customers(request):
    query = request.GET.get('q', '').strip()

    results = []
    if query:
        customers = Customer.objects.filter(
            is_active=True,
            name__icontains=query,
        ).order_by('name')[:10]

        results = [
            {
                'id': customer.id,
                'name': customer.name,
                'phone': customer.phone,
                'email': customer.email,
            }
            for customer in customers
        ]

    return JsonResponse({
        'success': True,
        'results': results,
    })


@require_POST
def pos_close_cash_register(request):
    cash_session = _get_cash_session(request)

    if not cash_session.get('is_open'):
        return JsonResponse({
            'success': False,
            'message': 'No hay una caja abierta para cerrar.',
        }, status=400)

    active_opening = CashOpening.objects.filter(
        station_name='caja actual 1',
        is_active=True,
    ).order_by('-opened_at').first()

    if not active_opening:
        return JsonResponse({
            'success': False,
            'message': 'No se encontró apertura activa.',
        }, status=400)

    counted_amount = Decimal('0.00')
    denomination_rows = []

    for denomination in _cash_denominations():
        field_name = f"denom_{str(denomination).replace('.', '_')}"
        units_count = int(request.POST.get(field_name, '0') or '0')
        subtotal = denomination * Decimal(units_count)

        denomination_rows.append({
            'denomination_value': denomination,
            'units_count': units_count,
            'subtotal': subtotal,
        })

        counted_amount += subtotal

    expected_amount = _safe_decimal(request.POST.get('expected_amount', '0.00'))
    allowed_variation = _safe_decimal(request.POST.get('allowed_variation', '5.00'))
    closing_comment = request.POST.get('closing_comment', '').strip()

    difference_amount = counted_amount - expected_amount
    unusual_case = abs(difference_amount) > allowed_variation

    closing = CashClosing.objects.create(
        cash_opening=active_opening,
        cashier_name=active_opening.cashier_name,
        expected_amount=expected_amount,
        counted_amount=counted_amount,
        difference_amount=difference_amount,
        allowed_variation=allowed_variation,
        unusual_case=unusual_case,
        closing_comment=closing_comment,
        closed_at=timezone.now(),
    )

    for row in denomination_rows:
        if row['units_count'] > 0:
            CashClosingDenomination.objects.create(
                cash_closing=closing,
                denomination_value=row['denomination_value'],
                units_count=row['units_count'],
                subtotal=row['subtotal'],
            )

    active_opening.is_active = False
    active_opening.save(update_fields=['is_active', 'updated_at'])

    cash_session['is_open'] = False
    cash_session['current_ticket_number'] = ''
    cash_session['opened_at'] = ''
    cash_session['opening_amount'] = '0.00'
    _save_cash_session(request, cash_session)

    return JsonResponse({
        'success': True,
        'message': 'Caja cerrada correctamente.',
        'cash_state': 'closed',
        'button_label': 'Abrir caja',
        'current_ticket_number': '',
        'counted_amount': f'{float(counted_amount):.2f}',
        'expected_amount': f'{float(expected_amount):.2f}',
        'difference_amount': f'{float(difference_amount):.2f}',
        'unusual_case': unusual_case,
        'cash_closing_id': closing.id,
    })


@require_POST
def pos_create_remittance(request):
    cash_session = _get_cash_session(request)

    if not cash_session.get('is_open'):
        return JsonResponse({
            'success': False,
            'message': 'No hay una caja abierta para remesar.',
        }, status=400)

    active_opening = CashOpening.objects.filter(
        station_name='caja actual 1',
        is_active=True,
    ).order_by('-opened_at').first()

    if not active_opening:
        return JsonResponse({
            'success': False,
            'message': 'No se encontró apertura activa.',
        }, status=400)

    password = request.POST.get('password', '').strip()
    receiver_name = request.POST.get('receiver_name', '').strip()
    receiver_doi = request.POST.get('receiver_doi', '').strip()
    destination = request.POST.get('destination', 'bank').strip()
    notes = request.POST.get('notes', '').strip()

    if not password:
        return JsonResponse({
            'success': False,
            'message': 'La contraseña es obligatoria para remesar.',
        }, status=400)

    if not receiver_name:
        return JsonResponse({
            'success': False,
            'message': 'Debes indicar quién recibe la remesa.',
        }, status=400)

    counted_amount = Decimal('0.00')
    denomination_rows = []

    for denomination in _cash_denominations():
        field_name = f"denom_{str(denomination).replace('.', '_')}"
        units_count = int(request.POST.get(field_name, '0') or '0')
        subtotal = denomination * Decimal(units_count)

        denomination_rows.append({
            'denomination_value': denomination,
            'units_count': units_count,
            'subtotal': subtotal,
        })

        counted_amount += subtotal

    if counted_amount <= Decimal('0.00'):
        return JsonResponse({
            'success': False,
            'message': 'La remesa debe ser mayor a $0.00.',
        }, status=400)

    remittance = CashRemittance.objects.create(
        cash_opening=active_opening,
        cashier_name=active_opening.cashier_name,
        authorized_by=active_opening.cashier_name,
        password_snapshot=password,
        total_amount=counted_amount,
        receiver_name=receiver_name,
        receiver_doi=receiver_doi,
        destination=destination if destination in ['bank', 'cash_general', 'other'] else 'other',
        remittance_started_at=timezone.now(),
        remittance_completed_at=timezone.now(),
        notes=notes,
    )

    for row in denomination_rows:
        if row['units_count'] > 0:
            CashRemittanceDenomination.objects.create(
                cash_remittance=remittance,
                denomination_value=row['denomination_value'],
                units_count=row['units_count'],
                subtotal=row['subtotal'],
            )

    return JsonResponse({
        'success': True,
        'message': 'Remesa registrada correctamente.',
        'remittance_id': remittance.id,
        'total_amount': f'{float(remittance.total_amount):.2f}',
        'receiver_name': remittance.receiver_name,
        'destination': remittance.destination,
    })

@require_POST
def pos_select_customer(request):
    customer_id = request.POST.get('customer_id')
    draft = _get_pos_draft(request)

    if not customer_id:
        return JsonResponse({
            'success': False,
            'message': 'Cliente inválido.',
        }, status=400)

    customer = get_object_or_404(Customer, id=customer_id, is_active=True)

    draft['mode'] = 'customer'
    draft['customer_id'] = customer.id
    draft['customer_name'] = customer.name

    _save_pos_draft(request, draft)

    return JsonResponse({
        'success': True,
        'customer_id': customer.id,
        'customer_name': customer.name,
        'mode': draft['mode'],
    })


@require_POST
def pos_quick_create_customer(request):
    name = request.POST.get('name', '').strip()
    phone = request.POST.get('phone', '').strip()
    email = request.POST.get('email', '').strip()

    if not name:
        return JsonResponse({
            'success': False,
            'message': 'El nombre del cliente es obligatorio.',
        }, status=400)

    customer = Customer.objects.create(
        name=name,
        phone=phone,
        email=email,
        customer_type='normal',
        is_active=True,
        notes='Cliente creado desde POS',
    )

    draft = _get_pos_draft(request)
    draft['mode'] = 'customer'
    draft['customer_id'] = customer.id
    draft['customer_name'] = customer.name
    _save_pos_draft(request, draft)

    return JsonResponse({
        'success': True,
        'customer_id': customer.id,
        'customer_name': customer.name,
        'mode': 'customer',
    })


def pos_search_products(request):
    query = request.GET.get('q', '').strip()

    results = []
    if query:
        products = Product.objects.filter(is_active=True).filter(
            name__icontains=query
        ).order_by('name')[:10]

        sku_products = Product.objects.filter(
            is_active=True,
            sku__icontains=query
        ).order_by('name')[:10]

        merged = []
        seen_ids = set()

        for product in list(products) + list(sku_products):
            if product.id not in seen_ids:
                merged.append(product)
                seen_ids.add(product.id)

        results = [
            {
                'id': product.id,
                'name': product.name,
                'sku': product.sku or '',
                'price': f"{_safe_decimal(product.price):.2f}",
                'product_type': product.product_type,
            }
            for product in merged[:10]
        ]

    return JsonResponse({
        'success': True,
        'results': results,
    })


@require_POST
def pos_add_product(request):
    product_id = request.POST.get('product_id')
    quantity = int(request.POST.get('quantity') or 1)

    if quantity < 1:
        quantity = 1

    draft = _get_pos_draft(request)

    if draft.get('mode') == 'customer' and not draft.get('customer_id'):
        return JsonResponse({
            'success': False,
            'message': 'Debes seleccionar un cliente antes de agregar productos.',
        }, status=400)

    product = get_object_or_404(Product, id=product_id, is_active=True)

    existing_item = None
    for item in draft.get('items', []):
        if int(item.get('product_id')) == product.id:
            existing_item = item
            break

    if existing_item:
        existing_item['quantity'] = int(existing_item.get('quantity', 0)) + quantity
    else:
        draft['items'].append({
            'product_id': product.id,
            'name': product.name,
            'sku': product.sku or '',
            'quantity': quantity,
            'price': f"{_safe_decimal(product.price):.2f}",
            'discount': '0.00',
            'subtotal': f"{_safe_decimal(product.price) * quantity:.2f}",
        })

    _save_pos_draft(request, draft)
    draft = _get_pos_draft(request)

    return JsonResponse({
        'success': True,
        'message': 'Producto agregado.',
        'items': draft['items'],
        'total_items': draft['total_items'],
        'total_amount': draft['total_amount'],
    })


@require_POST
def pos_update_quantity(request, product_id):
    quantity = int(request.POST.get('quantity') or 1)
    if quantity < 1:
        quantity = 1

    draft = _get_pos_draft(request)

    for item in draft.get('items', []):
        if int(item.get('product_id')) == int(product_id):
            item['quantity'] = quantity
            break

    _save_pos_draft(request, draft)
    draft = _get_pos_draft(request)

    return JsonResponse({
        'success': True,
        'items': draft['items'],
        'total_items': draft['total_items'],
        'total_amount': draft['total_amount'],
    })


@require_POST
def pos_remove_product(request, product_id):
    draft = _get_pos_draft(request)

    filtered_items = []
    for item in draft.get('items', []):
        if int(item.get('product_id')) != int(product_id):
            filtered_items.append(item)

    draft['items'] = filtered_items

    _save_pos_draft(request, draft)
    draft = _get_pos_draft(request)

    return JsonResponse({
        'success': True,
        'message': 'Producto eliminado.',
        'items': draft['items'],
        'total_items': draft['total_items'],
        'total_amount': draft['total_amount'],
    })


@require_POST
def pos_clear_draft(request):
    draft = _empty_pos_draft()
    _save_pos_draft(request, draft)

    return JsonResponse({
        'success': True,
        'message': 'Venta temporal limpiada.',
        'items': [],
        'total_items': 0,
        'total_amount': '0.00',
        'customer_name': '',
        'mode': 'customer',
    })


@require_POST
def pos_hold_slot_save(request):
    slot = request.POST.get('slot', '').strip()
    draft = _get_pos_draft(request)
    hold_slots = _get_hold_slots(request)

    if slot not in ['slot_1', 'slot_2', 'slot_3']:
        return JsonResponse({
            'success': False,
            'message': 'Espera inválida.',
        }, status=400)

    hold_slots[slot] = draft
    _save_hold_slots(request, hold_slots)
    _save_pos_draft(request, _empty_pos_draft())

    return JsonResponse({
        'success': True,
        'message': 'Venta enviada a espera.',
        'slot': slot,
        'occupied': hold_slots[slot] is not None,
    })


@require_POST
def pos_hold_slot_load(request):
    slot = request.POST.get('slot', '').strip()
    hold_slots = _get_hold_slots(request)

    if slot not in ['slot_1', 'slot_2', 'slot_3']:
        return JsonResponse({
            'success': False,
            'message': 'Espera inválida.',
        }, status=400)

    draft = hold_slots.get(slot)
    if not draft:
        return JsonResponse({
            'success': False,
            'message': 'La espera está vacía.',
        }, status=400)

    _save_pos_draft(request, draft)
    hold_slots[slot] = None
    _save_hold_slots(request, hold_slots)

    draft = _get_pos_draft(request)

    return JsonResponse({
        'success': True,
        'message': 'Venta recuperada desde espera.',
        'slot': slot,
        'draft': draft,
    })


def pos_hold_slots_status(request):
    hold_slots = _get_hold_slots(request)

    return JsonResponse({
        'success': True,
        'slots': {
            'slot_1': bool(hold_slots.get('slot_1')),
            'slot_2': bool(hold_slots.get('slot_2')),
            'slot_3': bool(hold_slots.get('slot_3')),
        }
    })


@require_POST
def pos_save_order(request):
    draft = _get_pos_draft(request)

    if not draft.get('document_type'):
        return JsonResponse({
            'success': False,
            'message': 'Debes seleccionar Ticket o CCF antes de guardar.',
        }, status=400)

    if not draft.get('items'):
        return JsonResponse({
            'success': False,
            'message': 'No hay productos en la venta.',
        }, status=400)

    if draft.get('mode') == 'customer':
        customer_id = draft.get('customer_id')
        if not customer_id:
            return JsonResponse({
                'success': False,
                'message': 'Debes seleccionar un cliente.',
            }, status=400)
        customer = get_object_or_404(Customer, id=customer_id, is_active=True)
    else:
        customer = Customer.objects.filter(name__iexact='Cliente General').first()
        if not customer:
            customer = Customer.objects.filter(customer_type='varios', is_active=True).first()

        if not customer:
            return JsonResponse({
                'success': False,
                'message': 'No existe cliente base para pedidos varios.',
            }, status=400)

    subtotal = Decimal('0.00')
    discount = Decimal('0.00')
    total = Decimal('0.00')

    for item in draft.get('items', []):
        subtotal += _safe_decimal(item.get('price')) * Decimal(item.get('quantity', 0))
        discount += _safe_decimal(item.get('discount'))
        total += _safe_decimal(item.get('subtotal'))

    saved_order = SavedOrder.objects.create(
        customer=customer,
        document_type=draft.get('document_type'),
        subtotal=subtotal,
        discount=discount,
        tax=Decimal('0.00'),
        total=total,
        is_active=True,
        notes='Pedido guardado desde POS',
    )

    for item in draft.get('items', []):
        product = get_object_or_404(Product, id=item.get('product_id'), is_active=True)

        SavedOrderItem.objects.create(
            saved_order=saved_order,
            product=product,
            quantity=_safe_decimal(item.get('quantity')),
            unit_price=_safe_decimal(item.get('price')),
            discount=_safe_decimal(item.get('discount')),
            subtotal=_safe_decimal(item.get('subtotal')),
        )

    cleaned_draft = _empty_pos_draft()
    _save_pos_draft(request, cleaned_draft)

    return JsonResponse({
        'success': True,
        'message': f'Pedido guardado correctamente. Pedido #{saved_order.id}',
        'saved_order_id': saved_order.id,
        'items': [],
        'total_items': 0,
        'total_amount': '0.00',
        'customer_name': '',
        'mode': 'customer',
        'document_type': '',
    })


def pos_saved_orders_list(request):
    query = request.GET.get('q', '').strip()

    orders = SavedOrder.objects.filter(is_active=True).select_related('customer').order_by('-created_at')

    if query:
        orders = [
            order for order in orders
            if query.lower() in str(order.id).lower() or query.lower() in order.customer.name.lower()
        ]

    results = [
        {
            'id': order.id,
            'customer_name': order.customer.name,
            'document_type': order.document_type,
            'total': f"{order.total:.2f}",
            'created_at': order.created_at.strftime('%Y-%m-%d %H:%M'),
        }
        for order in orders[:15]
    ]

    return JsonResponse({
        'success': True,
        'results': results,
    })


@require_POST
def pos_load_saved_order(request):
    order_id = request.POST.get('order_id')
    saved_order = get_object_or_404(SavedOrder, id=order_id)

    customer_name = saved_order.customer.name if saved_order.customer else 'Clientes varios'
    mode = 'customer' if saved_order.customer else 'varios'

    items = []
    total_items = 0

    for item in saved_order.items.all():
        quantity = int(item.quantity)
        price = float(item.unit_price)
        discount = float(item.discount)
        subtotal = float(item.subtotal)

        items.append({
            'product_id': item.product.id,
            'name': item.product.name,
            'quantity': quantity,
            'price': f'{price:.2f}',
            'discount': f'{discount:.2f}',
            'subtotal': f'{subtotal:.2f}',
        })

        total_items += quantity

    draft = {
        'customer_id': saved_order.customer.id if saved_order.customer else None,
        'customer_name': customer_name,
        'mode': mode,
        'document_type': saved_order.document_type,
        'items': items,
        'total_items': total_items,
        'total_amount': f'{float(saved_order.total):.2f}',
        'status': 'draft',
    }

    _save_pos_draft(request, draft)

    return JsonResponse({
        'success': True,
        'customer_name': customer_name,
        'mode': mode,
        'document_type': saved_order.document_type,
        'items': items,
        'total_items': total_items,
        'total_amount': f'{float(saved_order.total):.2f}',
    })


def pos_inventory_lookup(request):
    query = request.GET.get('q', '').strip()

    inventories = FinishedProductInventory.objects.select_related('product').order_by('product__name')

    if query:
        inventories = inventories.filter(
            Q(product__name__icontains=query) |
            Q(product__sku__icontains=query)
        )

    results = [
        {
            'product_id': inv.product.id,
            'product_name': inv.product.name,
            'sku': inv.product.sku or '',
            'quantity': f"{inv.quantity:.2f}",
            }
        for inv in inventories[:20]
    ]

    return JsonResponse({
        'success': True,
        'results': results,
    })


def pos_reprint_tickets_month(request):
    query = request.GET.get('q', '').strip()

    sales = Sale.objects.select_related('customer').order_by('-created_at')

    if query:
        sales = sales.filter(
            Q(id__icontains=query) |
            Q(customer__name__icontains=query)
        )

    results = [
        {
            'id': sale.id,
            'customer_name': sale.customer.name,
            'status': sale.status,
            'total': f"{sale.total:.2f}",
            'created_at': sale.created_at.strftime('%Y-%m-%d %H:%M'),
        }
        for sale in sales[:30]
    ]

    return JsonResponse({
        'success': True,
        'results': results,
    })

@require_POST
def pos_pay_sale(request):
    cash_session = _get_cash_session(request)
    draft = _get_pos_draft(request)

    if not cash_session.get('is_open'):
        return JsonResponse({
            'success': False,
            'message': 'No hay una caja abierta para cobrar.',
        }, status=400)

    if draft.get('document_type') not in ['ticket', 'ccf']:
        return JsonResponse({
            'success': False,
            'message': 'Debes seleccionar Ticket o CCF antes de cobrar.',
        }, status=400)

    if not draft.get('items'):
        return JsonResponse({
            'success': False,
            'message': 'No hay productos en la venta.',
        }, status=400)

    if draft.get('mode') == 'customer':
        customer_id = draft.get('customer_id')
        if not customer_id:
            return JsonResponse({
                'success': False,
                'message': 'Debes seleccionar un cliente.',
            }, status=400)

        customer = get_object_or_404(
            Customer,
            id=customer_id,
            is_active=True
        )
    else:
        customer = Customer.objects.filter(
            customer_type='varios',
            is_active=True
        ).first()

        if not customer:
            return JsonResponse({
                'success': False,
                'message': 'No existe cliente base para ventas varios.',
            }, status=400)

    active_opening = CashOpening.objects.filter(
        station_name='caja actual 1',
        is_active=True,
    ).order_by('-opened_at').first()

    if not active_opening:
        return JsonResponse({
            'success': False,
            'message': 'No existe apertura activa de caja.',
        }, status=400)

    amount_received = _safe_decimal(request.POST.get('amount_received', '0.00'))

    subtotal = Decimal('0.00')
    discount = Decimal('0.00')
    total = Decimal('0.00')

    for item in draft.get('items', []):
        quantity = _safe_decimal(item.get('quantity'))
        price = _safe_decimal(item.get('price'))
        item_discount = _safe_decimal(item.get('discount'))

        line_subtotal = (quantity * price) - item_discount

        subtotal += quantity * price
        discount += item_discount
        total += line_subtotal  # FIX: recalcular total real (no confiar en frontend)

    if amount_received < total:
        return JsonResponse({
            'success': False,
            'message': 'El efectivo recibido no cubre el total de la venta.',
        }, status=400)

    sale = Sale.objects.create(
        customer=customer,
        status='paid',
        subtotal=subtotal,
        discount=discount,
        tax=Decimal('0.00'),
        total=total,
        notes=f"Venta POS {draft.get('document_type', '').upper()} - estación {active_opening.station_name}",
    )

    for item in draft.get('items', []):
        product = get_object_or_404(Product, id=item.get('product_id'), is_active=True)

        quantity = _safe_decimal(item.get('quantity'))
        price = _safe_decimal(item.get('price'))
        item_discount = _safe_decimal(item.get('discount'))
        line_subtotal = (quantity * price) - item_discount

        SaleItem.objects.create(
            sale=sale,
            product=product,
            quantity=quantity,
            unit_price=price,
            discount=item_discount,
            subtotal=line_subtotal,  # FIX: recalculado backend
        )

    payment = Payment.objects.create(
        sale=sale,
        amount=total,
        method='cash',
        reference=f'POS-{sale.id}',
        notes='Cobro contado desde POS',
    )

    cash_account = Account.objects.filter(code='1.1.02', is_active=True).first()
    sales_income_account = Account.objects.filter(code='4.1.01', is_active=True).first()

    if not cash_account or not sales_income_account:
        return JsonResponse({
            'success': False,
            'message': 'Faltan cuentas contables base para registrar la venta.',
        }, status=400)

    journal_entry = JournalEntry.objects.create(
        reference=f'VENTA-POS-{sale.id}',
        description=f'Venta POS #{sale.id} al contado',
        entry_date=timezone.now().date(),
        status='posted',
    )

    JournalEntryLine.objects.create(
        journal_entry=journal_entry,
        account=cash_account,
        account_name=cash_account.name,
        entry_type='debit',
        amount=total,
        notes=f'Ingreso a caja por venta #{sale.id}',
    )

    JournalEntryLine.objects.create(
        journal_entry=journal_entry,
        account=sales_income_account,
        account_name=sales_income_account.name,
        entry_type='credit',
        amount=total,
        notes=f'Reconocimiento de ingreso por venta #{sale.id}',
    )

    change_amount = amount_received - total

    cleaned_draft = _empty_pos_draft()
    _save_pos_draft(request, cleaned_draft)

    current_ticket_number = cash_session.get('current_ticket_number', 'T-000001')
    next_number = 1

    if current_ticket_number.startswith('T-'):
        try:
            next_number = int(current_ticket_number.replace('T-', '')) + 1
        except ValueError:
            next_number = 2

    cash_session['current_ticket_number'] = f'T-{next_number:06d}'
    _save_cash_session(request, cash_session)

    return JsonResponse({
        'success': True,
        'message': 'Venta cobrada correctamente.',
        'sale_id': sale.id,
        'journal_entry_id': journal_entry.id,
        'payment_id': payment.id,  # FIX: evitar query innecesaria
        'total': f'{float(total):.2f}',
        'amount_received': f'{float(amount_received):.2f}',
        'change_amount': f'{float(change_amount):.2f}',
        'next_ticket_number': cash_session['current_ticket_number'],
        'document_type': draft.get('document_type', ''),
    })

@require_POST
def pos_credit_sale(request):
    cash_session = _get_cash_session(request)
    draft = _get_pos_draft(request)

    if not cash_session.get('is_open'):
        return JsonResponse({
            'success': False,
            'message': 'No hay una caja abierta para registrar crédito.',
        }, status=400)

    if draft.get('document_type') not in ['ticket', 'ccf']:
        return JsonResponse({
            'success': False,
            'message': 'Debes seleccionar Ticket o CCF antes de enviar a crédito.',
        }, status=400)

    if not draft.get('items'):
        return JsonResponse({
            'success': False,
            'message': 'No hay productos en la venta.',
        }, status=400)

    customer_id = draft.get('customer_id')
    if not customer_id:
        return JsonResponse({
            'success': False,
            'message': 'Debes seleccionar un cliente para crédito.',
        }, status=400)

    customer = get_object_or_404(Customer, id=customer_id, is_active=True)

    active_opening = CashOpening.objects.filter(
        station_name='caja actual 1',
        is_active=True,
    ).order_by('-opened_at').first()

    if not active_opening:
        return JsonResponse({
            'success': False,
            'message': 'No existe apertura activa de caja.',
        }, status=400)

    total = _safe_decimal(draft.get('total_amount', '0.00'))
    subtotal = Decimal('0.00')
    discount = Decimal('0.00')

    for item in draft.get('items', []):
        subtotal += _safe_decimal(item.get('price')) * Decimal(item.get('quantity', 0))
        discount += _safe_decimal(item.get('discount'))

    sale = Sale.objects.create(
        customer=customer,
        status='credit',
        subtotal=subtotal,
        discount=discount,
        tax=Decimal('0.00'),
        total=total,
        notes=f"Venta POS {draft.get('document_type', '').upper()} a crédito - estación {active_opening.station_name}",
    )

    for item in draft.get('items', []):
        product = get_object_or_404(Product, id=item.get('product_id'), is_active=True)

        SaleItem.objects.create(
            sale=sale,
            product=product,
            quantity=_safe_decimal(item.get('quantity')),
            unit_price=_safe_decimal(item.get('price')),
            discount=_safe_decimal(item.get('discount')),
            subtotal=_safe_decimal(item.get('subtotal')),
        )

    receivable = AccountReceivable.objects.create(
        customer=customer,
        reference=f'VENTA-CREDITO-{sale.id}',
        amount=total,
        due_date=timezone.now().date(),
        status='pending',
        notes=f'Cuenta por cobrar generada desde POS por venta #{sale.id}',
    )

    receivable_account = Account.objects.filter(code='1.1.04', is_active=True).first()
    sales_income_account = Account.objects.filter(code='4.1.01', is_active=True).first()

    if not receivable_account or not sales_income_account:
        return JsonResponse({
            'success': False,
            'message': 'Faltan cuentas contables base para registrar el crédito.',
        }, status=400)

    journal_entry = JournalEntry.objects.create(
        reference=f'VENTA-CREDITO-{sale.id}',
        description=f'Venta POS #{sale.id} a crédito',
        entry_date=timezone.now().date(),
        status='posted',
    )

    JournalEntryLine.objects.create(
        journal_entry=journal_entry,
        account=receivable_account,
        account_name=receivable_account.name,
        entry_type='debit',
        amount=total,
        notes=f'Cuenta por cobrar generada por venta #{sale.id}',
    )

    JournalEntryLine.objects.create(
        journal_entry=journal_entry,
        account=sales_income_account,
        account_name=sales_income_account.name,
        entry_type='credit',
        amount=total,
        notes=f'Reconocimiento de ingreso por venta a crédito #{sale.id}',
    )

    cleaned_draft = _empty_pos_draft()
    _save_pos_draft(request, cleaned_draft)

    current_ticket_number = cash_session.get('current_ticket_number', 'T-000001')
    next_number = 1

    if current_ticket_number.startswith('T-'):
        try:
            next_number = int(current_ticket_number.replace('T-', '')) + 1
        except ValueError:
            next_number = 2

    cash_session['current_ticket_number'] = f'T-{next_number:06d}'
    _save_cash_session(request, cash_session)

    return JsonResponse({
        'success': True,
        'message': 'Venta a crédito registrada correctamente.',
        'sale_id': sale.id,
        'receivable_id': receivable.id,
        'journal_entry_id': journal_entry.id,
        'total': f'{float(total):.2f}',
        'next_ticket_number': cash_session['current_ticket_number'],
        'document_type': draft.get('document_type', ''),
        'customer_name': customer.name,
    })

def sale_list(request):
    sales = Sale.objects.select_related('customer').all().order_by('-created_at')
    context = {
        'sales': sales,
    }
    return render(request, 'billing/sale_list.html', context)


def sale_manage(request):
    sales = Sale.objects.select_related('customer').all().order_by('-created_at')
    context = {
        'sales': sales,
    }
    return render(request, 'billing/sale_manage.html', context)


def sale_create(request):
    customers = Customer.objects.filter(is_active=True).order_by('name')

    if request.method == 'POST':
        Sale.objects.create(
            customer_id=request.POST.get('customer'),
            status=request.POST.get('status', 'draft'),
            subtotal=request.POST.get('subtotal') or 0,
            discount=request.POST.get('discount') or 0,
            tax=request.POST.get('tax') or 0,
            total=request.POST.get('total') or 0,
            notes=request.POST.get('notes', ''),
        )
        return redirect('sale_list')

    context = {
        'customers': customers,
    }
    return render(request, 'billing/sale_form.html', context)


def sale_update(request, sale_id):
    sale = get_object_or_404(Sale, id=sale_id)
    customers = Customer.objects.filter(is_active=True).order_by('name')

    if request.method == 'POST':
        sale.customer_id = request.POST.get('customer')
        sale.status = request.POST.get('status', 'draft')
        sale.subtotal = request.POST.get('subtotal') or 0
        sale.discount = request.POST.get('discount') or 0
        sale.tax = request.POST.get('tax') or 0
        sale.total = request.POST.get('total') or 0
        sale.notes = request.POST.get('notes', '')
        sale.save()
        return redirect('sale_manage')

    context = {
        'sale': sale,
        'customers': customers,
    }
    return render(request, 'billing/sale_form.html', context)


def sale_delete(request, sale_id):
    sale = get_object_or_404(Sale, id=sale_id)

    if request.method == 'POST':
        sale.delete()
        return redirect('sale_manage')

    context = {
        'sale': sale,
    }
    return render(request, 'billing/sale_delete.html', context)