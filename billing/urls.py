from django.urls import path
from .views import (
    sale_home,
    sale_list,
    sale_manage,
    sale_create,
    sale_update,
    sale_delete,
    pos_set_mode,
    pos_set_document_type,
    pos_close_cash_session,
    pos_search_customers,
    pos_select_customer,
    pos_quick_create_customer,
    pos_search_products,
    pos_add_product,
    pos_update_quantity,
    pos_remove_product,
    pos_clear_draft,
    pos_hold_slot_save,
    pos_hold_slot_load,
    pos_hold_slots_status,
    pos_save_order,
    pos_saved_orders_list,
    pos_load_saved_order,
    pos_inventory_lookup,
    pos_reprint_tickets_month,
    pos_open_cash_register,
    pos_close_cash_register,
    pos_create_remittance,
    pos_pay_sale,
    pos_credit_sale
)

urlpatterns = [
    path('', sale_home, name='sale_home'),
    path('list/', sale_list, name='sale_list'),
    path('manage/', sale_manage, name='sale_manage'),
    path('create/', sale_create, name='sale_create'),
    path('edit/<int:sale_id>/', sale_update, name='sale_update'),
    path('delete/<int:sale_id>/', sale_delete, name='sale_delete'),

    path('pos/set-mode/', pos_set_mode, name='pos_set_mode'),
    path('pos/set-document-type/', pos_set_document_type, name='pos_set_document_type'),

    path('pos/close-cash-session/', pos_close_cash_session, name='pos_close_cash_session'),

    path('pos/search-customers/', pos_search_customers, name='pos_search_customers'),
    path('pos/select-customer/', pos_select_customer, name='pos_select_customer'),
    path('pos/quick-create-customer/', pos_quick_create_customer, name='pos_quick_create_customer'),

    path('pos/search-products/', pos_search_products, name='pos_search_products'),
    path('pos/add-product/', pos_add_product, name='pos_add_product'),
    path('pos/update-quantity/<int:product_id>/', pos_update_quantity, name='pos_update_quantity'),
    path('pos/remove-product/<int:product_id>/', pos_remove_product, name='pos_remove_product'),
    path('pos/clear-draft/', pos_clear_draft, name='pos_clear_draft'),

    path('pos/hold-slot-save/', pos_hold_slot_save, name='pos_hold_slot_save'),
    path('pos/hold-slot-load/', pos_hold_slot_load, name='pos_hold_slot_load'),
    path('pos/hold-slots-status/', pos_hold_slots_status, name='pos_hold_slots_status'),

    path('pos/save-order/', pos_save_order, name='pos_save_order'),
    path('pos/saved-orders/', pos_saved_orders_list, name='pos_saved_orders_list'),
    path('pos/load-saved-order/', pos_load_saved_order, name='pos_load_saved_order'),

    path('pos/inventory-lookup/', pos_inventory_lookup, name='pos_inventory_lookup'),
    path('pos/reprint-tickets-month/', pos_reprint_tickets_month, name='pos_reprint_tickets_month'),
    path('pos/open-cash-register/', pos_open_cash_register, name='pos_open_cash_register'),
    path('pos/close-cash-register/', pos_close_cash_register, name='pos_close_cash_register'),
    path('pos/create-remittance/', pos_create_remittance, name='pos_create_remittance'),
    path('pos/pay-sale/', pos_pay_sale, name='pos_pay_sale'),
    path('pos/credit-sale/', pos_credit_sale, name='pos_credit_sale'),
]
