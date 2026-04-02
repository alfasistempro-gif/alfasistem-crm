from django.db import models
from core.models import TimeStampedModel
from customers.models import Customer
from catalog.models import Product


class Sale(TimeStampedModel):
    SALE_STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('credit', 'Credit'),
        ('cancelled', 'Cancelled'),
        ('on_hold', 'On hold'),
    ]

    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name='sales'
    )
    status = models.CharField(
        max_length=20,
        choices=SALE_STATUS_CHOICES,
        default='draft'
    )
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'

    def __str__(self):
        return f"Venta #{self.id} - {self.customer.name}"


class SaleItem(TimeStampedModel):
    sale = models.ForeignKey(
        Sale,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='sale_items'
    )
    quantity = models.DecimalField(max_digits=12, decimal_places=2, default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        ordering = ['id']
        verbose_name = 'Item de venta'
        verbose_name_plural = 'Items de venta'

    def __str__(self):
        return f"{self.product.name} - Venta #{self.sale.id}"


class Payment(TimeStampedModel):
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('transfer', 'Transfer'),
        ('credit', 'Credit'),
    ]

    sale = models.ForeignKey(
        Sale,
        on_delete=models.CASCADE,
        related_name='payments'
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default='cash'
    )
    reference = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'

    def __str__(self):
        return f"Pago #{self.id} - Venta #{self.sale.id}"


class SavedOrder(TimeStampedModel):
    DOCUMENT_TYPE_CHOICES = [
        ('ticket', 'Ticket'),
        ('ccf', 'CCF'),
    ]

    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name='saved_orders'
    )
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Pedido guardado'
        verbose_name_plural = 'Pedidos guardados'

    def __str__(self):
        return f"Pedido #{self.id} - {self.customer.name}"


class SavedOrderItem(TimeStampedModel):
    saved_order = models.ForeignKey(
        SavedOrder,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='saved_order_items'
    )
    quantity = models.DecimalField(max_digits=12, decimal_places=2, default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        ordering = ['id']
        verbose_name = 'Item de pedido guardado'
        verbose_name_plural = 'Items de pedidos guardados'

    def __str__(self):
        return f"{self.product.name} - Pedido #{self.saved_order.id}"


class CashOpening(TimeStampedModel):
    station_name = models.CharField(max_length=100, default='caja actual 1')
    sales_channel = models.CharField(max_length=100, default='canal de ventas 1')
    cashier_name = models.CharField(max_length=150)
    opening_password_snapshot = models.CharField(max_length=255, blank=True)
    opening_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    opened_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-opened_at']
        verbose_name = 'Apertura de caja'
        verbose_name_plural = 'Aperturas de caja'

    def __str__(self):
        return f"Apertura #{self.id} - {self.station_name} - {self.cashier_name}"


class CashClosing(TimeStampedModel):
    cash_opening = models.ForeignKey(
        CashOpening,
        on_delete=models.PROTECT,
        related_name='closings'
    )
    cashier_name = models.CharField(max_length=150)
    expected_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    counted_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    difference_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    allowed_variation = models.DecimalField(max_digits=12, decimal_places=2, default=5)
    unusual_case = models.BooleanField(default=False)
    closing_comment = models.TextField(blank=True)
    closed_at = models.DateTimeField()

    class Meta:
        ordering = ['-closed_at']
        verbose_name = 'Cierre de caja'
        verbose_name_plural = 'Cierres de caja'

    def __str__(self):
        return f"Cierre #{self.id} - {self.cash_opening.station_name}"


class CashClosingDenomination(TimeStampedModel):
    cash_closing = models.ForeignKey(
        CashClosing,
        on_delete=models.CASCADE,
        related_name='denominations'
    )
    denomination_value = models.DecimalField(max_digits=12, decimal_places=2)
    units_count = models.PositiveIntegerField(default=0)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        ordering = ['denomination_value']
        verbose_name = 'Denominación de cierre'
        verbose_name_plural = 'Denominaciones de cierre'

    def __str__(self):
        return f"{self.denomination_value} x {self.units_count}"


class CashRemittance(TimeStampedModel):
    DESTINATION_CHOICES = [
        ('bank', 'Bank'),
        ('cash_general', 'Cash General'),
        ('other', 'Other'),
    ]

    cash_opening = models.ForeignKey(
        CashOpening,
        on_delete=models.PROTECT,
        related_name='remittances'
    )
    cashier_name = models.CharField(max_length=150)
    authorized_by = models.CharField(max_length=150, blank=True)
    password_snapshot = models.CharField(max_length=255, blank=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    receiver_name = models.CharField(max_length=150)
    receiver_doi = models.CharField(max_length=50, blank=True)
    destination = models.CharField(max_length=30, choices=DESTINATION_CHOICES, default='bank')
    remittance_started_at = models.DateTimeField()
    remittance_completed_at = models.DateTimeField()
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-remittance_completed_at']
        verbose_name = 'Remesa'
        verbose_name_plural = 'Remesas'

    def __str__(self):
        return f"Remesa #{self.id} - {self.cash_opening.station_name}"


class CashRemittanceDenomination(TimeStampedModel):
    cash_remittance = models.ForeignKey(
        CashRemittance,
        on_delete=models.CASCADE,
        related_name='denominations'
    )
    denomination_value = models.DecimalField(max_digits=12, decimal_places=2)
    units_count = models.PositiveIntegerField(default=0)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        ordering = ['denomination_value']
        verbose_name = 'Denominación de remesa'
        verbose_name_plural = 'Denominaciones de remesa'

    def __str__(self):
        return f"{self.denomination_value} x {self.units_count}"