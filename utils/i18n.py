# utils/i18n.py
"""
Simple translation system for Stock Manager with RTL support.
"""
import os
import json
try:
    import arabic_reshaper
    from bidi.algorithm import get_display as _bidi_display
    _HAS_ARABIC_SHAPING = True
except ImportError:                       # libs not installed → no-op
    _HAS_ARABIC_SHAPING = False
    _bidi_display = None
    arabic_reshaper = None
CONFIG_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), 'settings.json'
)

LANGUAGES = {
    'en': 'English',
    'fr': 'Français',
    'ar': 'العربية',
}

RTL_LANGUAGES = {'ar'}

_current = 'fr'


TRANSLATIONS = {
    # =====================================================================
    # ENGLISH
    # =====================================================================
    'en': {
        'app.title': 'Stock Manager',
        'app.window_title': 'Stock Manager — {username} ({role})',
        'nav.sales': 'Sales',
        'nav.products': 'Products',
        'nav.history': 'History',
        'nav.reports': 'Reports',
        'nav.users': 'Users',
        'nav.deleted': 'Trash',
        'nav.back_to_sales': '← Sales',
        'nav.back_to_products': '← Products',
        'nav.back_to_history': '← History',
        'nav.reports_arrow': 'Reports →',
        'nav.users_arrow': 'Users →',
        'nav.products_arrow': 'Products →',
        'nav.sales_arrow': 'Sales →',

        'role.owner': 'Owner',
        'role.cashier': 'Cashier',

        'login.title': 'Login',
        'login.subtitle': 'Please log in',
        'login.username': 'Username:',
        'login.password': 'Password:',
        'login.connect': 'Log in',
        'login.language': 'Language:',
        'login.error_empty': 'Please enter your credentials',
        'login.error_invalid': 'Invalid credentials',

        'btn.add': 'Add',
        'btn.modify': 'Modify',
        'btn.clear': 'Clear',
        'btn.delete': 'Delete',
        'btn.cancel': 'Cancel',
        'btn.close': 'Close',
        'btn.save': 'Save',
        'btn.filter': 'Filter',
        'btn.clear_filter': 'Clear filter',
        'btn.refresh': '↻',
        'btn.verify': '🔍 Verify',
        'btn.details': 'Details',
        'btn.details_sale': 'Sale details',
        'btn.choose_photo': 'Choose Photo',
        'btn.add_stock': 'Add stock',
        'btn.delete_selection': 'Delete selection',
        'btn.ok': 'OK',
        'btn.yes': 'Yes',
        'btn.no': 'No',

        'lbl.total': 'Total',
        'lbl.profit': 'Profit',
        'lbl.sales_count': 'Sales',
        'lbl.date': 'Date',
        'lbl.time': 'Time',
        'lbl.quantity': 'Quantity',
        'lbl.unit': 'Unit',
        'lbl.article': 'Item',
        'lbl.articles': 'Items',
        'lbl.product': 'Product',
        'lbl.products': 'Products',
        'lbl.from': 'From:',
        'lbl.to': 'To:',
        'lbl.period': 'Period',
        'lbl.by': 'By',

        'unit.piece': 'piece',
        'unit.gram': 'gram',
        'unit.pack': 'pack',
        'unit.cigarette': 'cigarette',
        'unit.pieces': 'pcs',
        'unit.packs_short': 'pk',
        'unit.pieces_short': 'pc',
        'unit.units': 'units',
        'unit.unit_price': 'Unit price:',

        'msg.success': 'Success',
        'msg.error': 'Error',
        'msg.warning': 'Warning',
        'msg.info': 'Info',
        'msg.confirmation': 'Confirmation',
        'msg.access_denied': 'Access denied',
        'msg.no_permission': 'Permission denied.',
        'msg.invalid_numbers': 'Please enter valid numbers',
        'msg.stock_insufficient': 'Insufficient stock! Available: {available}',
        'msg.stock_only': 'Stock: {stock} only!',

        'sales.title': 'SALES',
        'sales.scanner_search': 'SCANNER / SEARCH',
        'sales.hint_scan': '📷 Digits = scan',
        'sales.hint_search': '🔍 Letters = search',
        'sales.telecom': 'TELECOM',
        'sales.telecom_shortcuts': 'TÉLÉCOM  [F1 – F6]',
        'sales.cart': 'CART',
        'sales.cart_pay_hint': '[SPACE] = Pay',
        'sales.btn_remove': 'Remove',
        'sales.btn_clear': 'Clear',
        'sales.btn_pay': '[SPACE] Pay',
        'sales.state_scan': '📷 SCAN — F1-F6=Télécom | Letters=Search | SPACE=Pay',
        'sales.state_searching': '🔍 SEARCH — ↑↓ navigate | Enter select',
        'sales.state_popup': '🪟 POPUP — Quantity | U=Unit | Enter=OK | ESC=Close',
        'sales.shortcuts_bar': ' [F1-F6] Télécom • [SPACE] Pay • [ESC] Cancel',
        'sales.not_found': 'Not found',
        'sales.cart_empty': 'Cart is empty',
        'sales.added': 'Added {name}',
        'sales.added_qty': 'Added {qty:g} {unit}',
        'sales.cash_in': 'Paid: {total:.2f} DT',
        'sales.save_error': 'Could not save sale:\n{e}',
        'sales.popup_weight_title': 'Sold by weight',
        'sales.popup_pack_title': 'Sold by pack',
        'sales.popup_cigarette_title': 'Cigarettes',
        'sales.price': 'Price',
        'sales.price_per_kg': 'Price: {p:.2f} DT/kg',
        'sales.pack_price': 'Pack price : {p:.2f} DT',
        'sales.unit_price': 'Unit price: {p:.2f} DT',
        'sales.stock_cigarettes': 'Stock: {n} cigarettes',
        'sales.sell_in': 'Sell as:',
        'sales.opt_packs': 'Packs',
        'sales.opt_units': 'Units',
        'sales.opt_grams': 'Grams (g)',
        'sales.opt_kilograms': 'Kilograms (kg)',
        'sales.qty': 'Quantity:',
        'sales.popup_hint': '[U] Change unit   •   [Enter] Add   •   [ESC] Cancel',
        'sales.not_found_full': 'Not found: {name}',

        'products.title': 'PRODUCTS',
        'products.add_modify': 'Add / Modify',
        'products.barcode': 'Barcode:',
        'products.name': 'Name:',
        'products.buy_price': 'Buy price:',
        'products.sell_price': 'Sell price:',
        'products.stock': 'Stock:',
        'products.unit_label': 'Unit:',
        'products.unit_piece': 'Piece',
        'products.unit_gram': 'Gram',
        'products.unit_pack': 'Pack',
        'products.unit_cigarette': 'Cigarette',
        'products.single_price': 'Unit price:',
        'products.pieces_per_pack': 'Pieces/Pack:',
        'products.cigarette_price': 'Cig. price:',
        'products.cig_stock_hint': 'Stock in INDIVIDUAL CIGARETTES\n(ex: 2000 = 100 packs)',
        'products.no_photo': 'No photo selected',
        'products.search': 'Search:',
        'products.col_id': 'ID',
        'products.col_barcode': 'Barcode',
        'products.col_name': 'Name',
        'products.col_buy': 'Buy',
        'products.col_sell': 'Sell',
        'products.col_unit': 'Unit',
        'products.col_stock': 'Stock',
        'products.col_type': 'Type',
        'products.success_added': 'Product added!',
        'products.success_updated': 'Product modified!',
        'products.confirm_delete': 'Delete this product?',
        'products.select_first': 'Select a product first',
        'products.name_required': 'Product name is required',
        'products.sell_gt_buy': 'Sell price must be greater than buy price',
        'products.pieces_gt_zero': 'Pieces/Pack must be greater than 0',
        'products.add_stock_title': 'Add to stock',
        'products.current_stock_pack': 'Current: {packs} packs + {pieces} pieces',
        'products.current_stock_cig': 'Current: {packs} packs + {units} units',
        'products.current_stock_g': 'Current: {stock} g',
        'products.current_stock': 'Current: {stock}',
        'products.add_packs': 'Add packs:',
        'products.add_pieces': 'Add pieces:',
        'products.add_cig': 'Add in individual cigarettes:',
        'products.add_cig_hint': '(ex: 20 = 1 pack)',
        'products.add_g': 'Add grams:',
        'products.qty_to_add': 'Quantity to add:',
        'products.positive_number': 'Please enter a positive number',
        'products.stock_added': 'Stock added',
        'products.owner_only': 'Only the owner can manage products.',

        'history.title': 'HISTORY',
        'history.deleted_btn': '🗑️ Trash',
        'history.col_date': 'Date',
        'history.col_time': 'Time',
        'history.col_count': 'Items',
        'history.col_total': 'Total (DT)',
        'history.col_profit': 'Profit (DT)',
        'history.btn_soft_delete': 'Delete (soft)',
        'history.btn_hard_delete': 'Delete permanently',
        'history.hint': '⚠️ Soft = hidden + stock restored • Hard = irreversible',
        'history.select_to_delete': 'Select one or more sales to delete',
        'history.confirm_soft': 'Delete {n} sale(s)?\nSale will be hidden and stock restored.',
        'history.confirm_hard': 'Permanently delete {n} sale(s)?\nThis action is irreversible.',
        'history.deleted_ok': '{n} sale(s) deleted',
        'history.owner_only_hard': 'Only the owner can permanently delete.',
        'history.select_sale': 'Select a sale',
        'history.no_items': 'This sale no longer has items.',
        'history.details_title': 'Details - {ts}',
        'history.sale_of': 'Sale of {ts}',
        'history.col_id': 'ID',
        'history.col_product': 'Product',
        'history.col_qty': 'Quantity',
        'history.col_unit': 'Unit',
        'history.delete_item': 'Delete selected item',
        'history.delete_item_confirm': 'Delete this item? Stock will be restored.',
        'history.delete_item_confirm_hard': 'PERMANENTLY delete this item?\nThis is irreversible.',
        'history.verify_total': 'Actual total: {t:.2f} DT',
        'history.verify_grouped': 'Grouped total: {t:.2f} DT',
        'history.verify_profit': 'Actual profit: {p:.2f} DT',
        'history.verify_grouped_profit': 'Grouped profit: {p:.2f} DT',
        'history.verify_ok': '✅ Consistent',
        'history.verify_bad': '⚠️ Inconsistency detected!',
        'history.verify_title': 'Verification',

        'deleted.title': 'TRASH — DELETED SALES',
        'deleted.deleted_from': 'Deleted from:',
        'deleted.to': 'to:',
        'deleted.filter': 'Filter',
        'deleted.view_all': 'View all',
        'deleted.col_deleted_at': 'Deleted on',
        'deleted.col_time': 'Time',
        'deleted.col_by': 'By',
        'deleted.col_items': 'Items',
        'deleted.col_total': 'Total (DT)',
        'deleted.col_profit': 'Profit (DT)',
        'deleted.restore_selection': 'Restore selection',
        'deleted.select_to_restore': 'Select one or more entries to restore',
        'deleted.confirm_restore': 'Restore {n} group(s) of deleted sales?\nSales will return to history and stock adjusted.',
        'deleted.restore_ok': '{n} group(s) restored',
        'deleted.details_title': 'Deleted sales on {ts}',
        'deleted.deleted_on': 'Deleted on {ts}',
        'deleted.col_sale_of': 'Sale of',
        'deleted.col_reason': 'Reason',
        'deleted.restore_one': 'Restore selected item',
        'deleted.confirm_restore_one': 'Restore this item?\nIt will return to history and stock adjusted.',
        'deleted.nothing_to_show': 'Nothing to show for this entry.',
        'deleted.no_more_items': 'No more items for this entry.',
        'deleted.select_item': 'Select an item',
        'deleted.unknown_user': '(unknown)',

        'reports.title': 'REPORTS',
        'reports.tab_summary': '📊 Sales summary',
        'reports.tab_products': '🏆 Top products',
        'reports.tab_stock': '📦 Stock status',
        'reports.tab_export': '📄 Export report',
        'reports.period': 'Period',
        'reports.load_summary': 'Load summary',
        'reports.today': 'Today',
        'reports.summary_header': 'SUMMARY FROM {start} TO {end}',
        'reports.total_sales': 'Total sales',
        'reports.total_profit': 'Total profit',
        'reports.transactions': 'Transactions',
        'reports.period_optional': 'Period (optional)',
        'reports.num_products': 'Number of products:',
        'reports.load_top': 'Load top products',
        'reports.clear_period': 'Clear period',
        'reports.col_product': 'Product',
        'reports.col_qty': 'Quantity',
        'reports.col_revenue': 'Revenue (DT)',
        'reports.col_profit': 'Profit (DT)',
        'reports.low_stock_threshold': 'Low stock threshold:',
        'reports.refresh_btn': 'Refresh',
        'reports.stock_value': "Total stock value (buy price) : {v:.2f} DT",
        'reports.low_stock_header': '⚠️  LOW STOCK PRODUCTS (threshold {t}) :',
        'reports.no_low_stock': '  None',
        'reports.report_period': 'Report period',
        'reports.generate': '📄 Generate report',
        'reports.from_last': '⏪ Since last report',
        'reports.open_folder': '📁 Open folder',
        'reports.preview': 'Preview',
        'reports.invalid_datetime': 'Invalid date/time format.',
        'reports.start_after_end': 'Start date is after end date.',
        'reports.no_previous': 'No previous report found.',
        'reports.corrupt_last': 'Last report file is corrupted.',
        'reports.cannot_open': 'Cannot open folder:\n{e}',
        'reports.cannot_write': 'Cannot write report:\n{e}',
        'reports.report_saved': 'Report saved to:\n{path}',
        'reports.report_title': '📋 PERIOD REPORT',
        'reports.report_from': 'From : {d}',
        'reports.report_to': 'To : {d}',
        'reports.report_generated': 'Generated on : {d}',
        'reports.report_by': 'By : {u}',
        'reports.report_sales_summary': '📊 SALES SUMMARY',
        'reports.report_total_sales': 'Total sales     : {v:>12.2f} DT',
        'reports.report_total_profit': 'Total profit    : {v:>12.2f} DT',
        'reports.report_num_trans': 'Number of transactions : {n:>10}',
        'reports.report_top10': '🏆 TOP 10 PRODUCTS',
        'reports.report_no_sales': '  No sales in this period.',
        'reports.report_stock': '📦 STOCK STATUS',
        'reports.report_stock_value': 'Total stock value : {v:.2f} DT',
        'reports.report_low_stock': '⚠️  LOW STOCK PRODUCTS (threshold {t})',
        'reports.report_none': '  None',
        'reports.report_hidden': '  ... and {n} other product(s) below threshold.',
        'reports.report_success': '✅ Report generated successfully',
        'reports.no_reports_yet': 'No reports generated yet.',

        'users.title': 'USERS',
        'users.add_user': 'Add user',
        'users.username': 'Username:',
        'users.full_name': 'Full name:',
        'users.password': 'Password:',
        'users.confirm': 'Confirm:',
        'users.role': 'Role:',
        'users.role_cashier': 'Cashier',
        'users.role_owner': 'Owner',
        'users.create': 'Create',
        'users.col_id': 'ID',
        'users.col_username': 'Username',
        'users.col_full_name': 'Full name',
        'users.col_role': 'Role',
        'users.col_active': 'Active',
        'users.col_created': 'Created on',
        'users.rename': 'Rename',
        'users.toggle_active': 'Activate / Deactivate',
        'users.change_password': 'Change password',
        'users.delete': 'Delete',
        'users.warn_owner': '⚠️ Do not delete the owner account.',
        'users.required_fields': 'Username and password required',
        'users.password_mismatch': 'Passwords do not match',
        'users.password_short': 'Password too short (min 4 chars)',
        'users.created_ok': "User '{u}' created",
        'users.select_user': 'Select a user',
        'users.rename_title': 'Rename - {u}',
        'users.new_name_for': "New name for '{u}':",
        'users.name_empty': 'Name cannot be empty',
        'users.renamed_ok': "Renamed to '{u}'",
        'users.cannot_disable_self': 'You cannot disable your own account',
        'users.cannot_delete_self': 'You cannot delete your own account',
        'users.confirm_delete': "Delete user '{u}'?",
        'users.password_new': 'New password:',
        'users.password_changed': 'Password changed',
        'users.active_yes': 'Yes',
        'users.active_no': 'No',

        'startup.no_screen': 'No accessible screen for this role.',
        'startup.permission_denied': "You don't have permission to open this screen.",
    },

    # =====================================================================
    # FRANÇAIS
    # =====================================================================
    'fr': {
        'app.title': 'Gestion de Stock',
        'app.window_title': 'Gestion de Stock — {username} ({role})',
        'nav.sales': 'Ventes',
        'nav.products': 'Produits',
        'nav.history': 'Historique',
        'nav.reports': 'Rapports',
        'nav.users': 'Utilisateurs',
        'nav.deleted': 'Corbeille',
        'nav.back_to_sales': '← Ventes',
        'nav.back_to_products': '← Produits',
        'nav.back_to_history': '← Historique',
        'nav.reports_arrow': 'Rapports →',
        'nav.users_arrow': 'Utilisateurs →',
        'nav.products_arrow': 'Produits →',
        'nav.sales_arrow': 'Ventes →',

        'role.owner': 'Propriétaire',
        'role.cashier': 'Caissier',

        'login.title': 'Connexion',
        'login.subtitle': 'Veuillez vous connecter',
        'login.username': 'Utilisateur:',
        'login.password': 'Mot de passe:',
        'login.connect': 'Se connecter',
        'login.language': 'Langue:',
        'login.error_empty': 'Veuillez saisir vos identifiants',
        'login.error_invalid': 'Identifiants invalides',

        'btn.add': 'Ajouter',
        'btn.modify': 'Modifier',
        'btn.clear': 'Effacer',
        'btn.delete': 'Supprimer',
        'btn.cancel': 'Annuler',
        'btn.close': 'Fermer',
        'btn.save': 'Enregistrer',
        'btn.filter': 'Filtrer',
        'btn.clear_filter': 'Effacer filtre',
        'btn.refresh': '↻',
        'btn.verify': '🔍 Vérifier',
        'btn.details': 'Détails',
        'btn.details_sale': 'Détails vente',
        'btn.choose_photo': 'Choisir Photo',
        'btn.add_stock': 'Ajouter stock',
        'btn.delete_selection': 'Supprimer sélection',
        'btn.ok': 'OK',
        'btn.yes': 'Oui',
        'btn.no': 'Non',

        'lbl.total': 'Total',
        'lbl.profit': 'Bénéfice',
        'lbl.sales_count': 'Ventes',
        'lbl.date': 'Date',
        'lbl.time': 'Heure',
        'lbl.quantity': 'Quantité',
        'lbl.unit': 'Unité',
        'lbl.article': 'Article',
        'lbl.articles': 'Articles',
        'lbl.product': 'Produit',
        'lbl.products': 'Produits',
        'lbl.from': 'Du:',
        'lbl.to': 'Au:',
        'lbl.period': 'Période',
        'lbl.by': 'Par',

        'unit.piece': 'pièce',
        'unit.gram': 'gramme',
        'unit.pack': 'pack',
        'unit.cigarette': 'cigarette',
        'unit.pieces': 'pcs',
        'unit.packs_short': 'pk',
        'unit.pieces_short': 'pc',
        'unit.units': 'unités',
        'unit.unit_price': 'Prix unitaire:',

        'msg.success': 'Succès',
        'msg.error': 'Erreur',
        'msg.warning': 'Attention',
        'msg.info': 'Info',
        'msg.confirmation': 'Confirmation',
        'msg.access_denied': 'Accès refusé',
        'msg.no_permission': 'Permission refusée.',
        'msg.invalid_numbers': 'Veuillez entrer des nombres valides',
        'msg.stock_insufficient': 'Stock insuffisant! Disponible: {available}',
        'msg.stock_only': 'Stock: {stock} seulement!',

        'sales.title': 'VENTES',
        'sales.scanner_search': 'SCANNER / RECHERCHER',
        'sales.hint_scan': '📷 Chiffres = scan',
        'sales.hint_search': '🔍 Lettres = recherche',
        'sales.telecom': 'TÉLÉCOM',
        'sales.telecom_shortcuts': 'TÉLÉCOM  [F1 – F6]',
        'sales.cart': 'PANIER',
        'sales.cart_pay_hint': '[ESPACE] = Payer',
        'sales.btn_remove': 'Retirer',
        'sales.btn_clear': 'Vider',
        'sales.btn_pay': '[ESPACE] Payer',
        'sales.state_scan': '📷 SCAN — F1-F6=Télécom | Lettres=Recherche | ESPACE=Payer',
        'sales.state_searching': '🔍 RECHERCHE — ↑↓ naviguer | Enter sélectionner',
        'sales.state_popup': '🪟 POPUP — Quantité | U=Unité | Enter=Valider | ESC=Fermer',
        'sales.shortcuts_bar': ' [F1-F6] Télécom • [ESPACE] Payer • [ESC] Annuler',
        'sales.not_found': 'Non trouvé',
        'sales.cart_empty': 'Panier vide',
        'sales.added': 'Ajouté {name}',
        'sales.added_qty': 'Ajouté {qty:g} {unit}',
        'sales.cash_in': 'Encaissé: {total:.2f} DT',
        'sales.save_error': "Impossible d'enregistrer la vente:\n{e}",
        'sales.popup_weight_title': 'Produit au poids',
        'sales.popup_pack_title': 'Produit en pack',
        'sales.popup_cigarette_title': 'Cigarettes',
        'sales.price': 'Prix',
        'sales.price_per_kg': 'Prix: {p:.2f} DT/kg',
        'sales.pack_price': 'Prix pack : {p:.2f} DT',
        'sales.unit_price': 'Prix unité: {p:.2f} DT',
        'sales.stock_cigarettes': 'Stock: {n} cigarettes',
        'sales.sell_in': 'Vendre en:',
        'sales.opt_packs': 'Packs',
        'sales.opt_units': 'Unités',
        'sales.opt_grams': 'Grammes (g)',
        'sales.opt_kilograms': 'Kilogrammes (kg)',
        'sales.qty': 'Quantité:',
        'sales.popup_hint': '[U] Changer unité   •   [Enter] Ajouter   •   [ESC] Annuler',
        'sales.not_found_full': 'Non trouvé: {name}',

        'products.title': 'PRODUITS',
        'products.add_modify': 'Ajouter / Modifier',
        'products.barcode': 'Code-barres:',
        'products.name': 'Nom:',
        'products.buy_price': "Prix d'achat:",
        'products.sell_price': 'Prix de vente:',
        'products.stock': 'Stock:',
        'products.unit_label': 'Unité:',
        'products.unit_piece': 'Pièce',
        'products.unit_gram': 'Gramme',
        'products.unit_pack': 'Pack',
        'products.unit_cigarette': 'Cigarette',
        'products.single_price': 'Prix unitaire:',
        'products.pieces_per_pack': 'Pièces/Pack:',
        'products.cigarette_price': 'Prix cigarette:',
        'products.cig_stock_hint': 'Stock en CIGARETTES INDIVIDUELLES\n(ex: 2000 = 100 packs)',
        'products.no_photo': 'Aucune photo sélectionnée',
        'products.search': 'Rechercher:',
        'products.col_id': 'ID',
        'products.col_barcode': 'Code-barres',
        'products.col_name': 'Nom',
        'products.col_buy': 'Achat',
        'products.col_sell': 'Vente',
        'products.col_unit': 'Unité',
        'products.col_stock': 'Stock',
        'products.col_type': 'Type',
        'products.success_added': 'Produit ajouté !',
        'products.success_updated': 'Produit modifié !',
        'products.confirm_delete': 'Supprimer ce produit ?',
        'products.select_first': "Sélectionnez un produit d'abord",
        'products.name_required': 'Le nom du produit est requis',
        'products.sell_gt_buy': "Le prix de vente doit être supérieur au prix d'achat",
        'products.pieces_gt_zero': 'Pièces/Pack doit être supérieur à 0',
        'products.add_stock_title': 'Ajouter au stock',
        'products.current_stock_pack': 'Stock actuel: {packs} packs + {pieces} pièces',
        'products.current_stock_cig': 'Stock actuel: {packs} packs + {units} unités',
        'products.current_stock_g': 'Stock actuel: {stock} g',
        'products.current_stock': 'Stock actuel: {stock}',
        'products.add_packs': 'Ajouter packs:',
        'products.add_pieces': 'Ajouter pièces:',
        'products.add_cig': 'Ajouter en cigarettes individuelles:',
        'products.add_cig_hint': '(ex: 20 = 1 pack)',
        'products.add_g': 'Ajouter grammes:',
        'products.qty_to_add': 'Quantité à ajouter:',
        'products.positive_number': 'Veuillez entrer un nombre positif',
        'products.stock_added': 'Stock ajouté',
        'products.owner_only': 'Seul le propriétaire peut gérer les produits.',

        'history.title': 'HISTORIQUE',
        'history.deleted_btn': '🗑️ Corbeille',
        'history.col_date': 'Date',
        'history.col_time': 'Heure',
        'history.col_count': 'Articles',
        'history.col_total': 'Total (DT)',
        'history.col_profit': 'Bénéfice (DT)',
        'history.btn_soft_delete': 'Supprimer (soft)',
        'history.btn_hard_delete': 'Supprimer définitivement',
        'history.hint': '⚠️ Soft = masquée + stock restauré • Hard = irréversible',
        'history.select_to_delete': 'Sélectionnez une ou plusieurs ventes à supprimer',
        'history.confirm_soft': 'Supprimer {n} vente(s) ?\nLa vente sera masquée et le stock restauré.',
        'history.confirm_hard': 'Supprimer DÉFINITIVEMENT {n} vente(s) ?\nCette action est irréversible.',
        'history.deleted_ok': '{n} vente(s) supprimée(s)',
        'history.owner_only_hard': 'Seul le propriétaire peut supprimer définitivement.',
        'history.select_sale': 'Sélectionnez une vente',
        'history.no_items': "Cette vente ne contient plus d'articles.",
        'history.details_title': 'Détails - {ts}',
        'history.sale_of': 'Vente du {ts}',
        'history.col_id': 'ID',
        'history.col_product': 'Produit',
        'history.col_qty': 'Quantité',
        'history.col_unit': 'Unité',
        'history.delete_item': "Supprimer l'article sélectionné",
        'history.delete_item_confirm': 'Supprimer cet article ? Le stock sera restauré.',
        'history.delete_item_confirm_hard': 'Supprimer DÉFINITIVEMENT cet article ?\nCette action est irréversible.',
        'history.verify_total': 'Total réel des ventes : {t:.2f} DT',
        'history.verify_grouped': 'Total groupé          : {t:.2f} DT',
        'history.verify_profit': 'Bénéfice réel         : {p:.2f} DT',
        'history.verify_grouped_profit': 'Bénéfice groupé       : {p:.2f} DT',
        'history.verify_ok': '✅ Cohérent',
        'history.verify_bad': '⚠️ Incohérence détectée!',
        'history.verify_title': 'Vérification',

        'deleted.title': 'CORBEILLE — VENTES SUPPRIMÉES',
        'deleted.deleted_from': 'Supprimé du:',
        'deleted.to': 'au:',
        'deleted.filter': 'Filtrer',
        'deleted.view_all': 'Tout voir',
        'deleted.col_deleted_at': 'Supprimé le',
        'deleted.col_time': 'Heure',
        'deleted.col_by': 'Par',
        'deleted.col_items': 'Articles',
        'deleted.col_total': 'Total (DT)',
        'deleted.col_profit': 'Bénéfice (DT)',
        'deleted.restore_selection': 'Restaurer la sélection',
        'deleted.select_to_restore': 'Sélectionnez une ou plusieurs entrées à restaurer',
        'deleted.confirm_restore': "Restaurer {n} groupe(s) de ventes supprimées ?\nLes ventes retourneront dans l'historique et le stock sera ajusté.",
        'deleted.restore_ok': '{n} groupe(s) restauré(s)',
        'deleted.details_title': 'Ventes supprimées le {ts}',
        'deleted.deleted_on': 'Supprimé le {ts}',
        'deleted.col_sale_of': 'Vente du',
        'deleted.col_reason': 'Raison',
        'deleted.restore_one': "Restaurer l'article sélectionné",
        'deleted.confirm_restore_one': "Restaurer cet article ?\nIl retournera dans l'historique et le stock sera ajusté.",
        'deleted.nothing_to_show': 'Rien à afficher pour cette entrée.',
        'deleted.no_more_items': 'Plus rien à afficher pour cette entrée.',
        'deleted.select_item': 'Sélectionnez un article',
        'deleted.unknown_user': '(inconnu)',

        'reports.title': 'RAPPORTS',
        'reports.tab_summary': '📊 Résumé ventes',
        'reports.tab_products': '🏆 Top produits',
        'reports.tab_stock': '📦 État stock',
        'reports.tab_export': '📄 Exporter rapport',
        'reports.period': 'Période',
        'reports.load_summary': 'Charger résumé',
        'reports.today': "Aujourd'hui",
        'reports.summary_header': 'RÉSUMÉ DU {start}  AU  {end}',
        'reports.total_sales': 'Total ventes',
        'reports.total_profit': 'Bénéfice total',
        'reports.transactions': 'Transactions',
        'reports.period_optional': 'Période (optionnelle)',
        'reports.num_products': 'Nombre de produits:',
        'reports.load_top': 'Charger top produits',
        'reports.clear_period': 'Effacer période',
        'reports.col_product': 'Produit',
        'reports.col_qty': 'Quantité',
        'reports.col_revenue': 'CA (DT)',
        'reports.col_profit': 'Bénéfice (DT)',
        'reports.low_stock_threshold': 'Seuil stock faible:',
        'reports.refresh_btn': 'Actualiser',
        'reports.stock_value': "Valeur totale du stock (prix d'achat) : {v:.2f} DT",
        'reports.low_stock_header': '⚠️  PRODUITS EN STOCK FAIBLE (seuil {t}) :',
        'reports.no_low_stock': '  Aucun',
        'reports.report_period': 'Période du rapport',
        'reports.generate': '📄 Générer rapport',
        'reports.from_last': '⏪ Depuis dernier rapport',
        'reports.open_folder': '📁 Ouvrir dossier',
        'reports.preview': 'Aperçu',
        'reports.invalid_datetime': 'Format date/heure invalide.',
        'reports.start_after_end': 'La date de début est après la date de fin.',
        'reports.no_previous': 'Aucun rapport précédent trouvé.',
        'reports.corrupt_last': 'Fichier du dernier rapport corrompu.',
        'reports.cannot_open': "Impossible d'ouvrir le dossier:\n{e}",
        'reports.cannot_write': "Impossible d'écrire le rapport:\n{e}",
        'reports.report_saved': 'Rapport sauvegardé dans :\n{path}',
        'reports.report_title': '📋 RAPPORT DE PÉRIODE',
        'reports.report_from': 'Du : {d}',
        'reports.report_to': 'Au : {d}',
        'reports.report_generated': 'Généré le : {d}',
        'reports.report_by': 'Par : {u}',
        'reports.report_sales_summary': '📊 RÉSUMÉ DES VENTES',
        'reports.report_total_sales': 'Total des ventes     : {v:>12.2f} DT',
        'reports.report_total_profit': 'Bénéfice total       : {v:>12.2f} DT',
        'reports.report_num_trans': 'Nombre de transactions : {n:>10}',
        'reports.report_top10': '🏆 TOP 10 PRODUITS',
        'reports.report_no_sales': '  Aucune vente sur cette période.',
        'reports.report_stock': '📦 ÉTAT DU STOCK',
        'reports.report_stock_value': 'Valeur totale du stock : {v:.2f} DT',
        'reports.report_low_stock': '⚠️  PRODUITS EN STOCK FAIBLE (seuil {t})',
        'reports.report_none': '  Aucun',
        'reports.report_hidden': '  ... et {n} autre(s) produit(s) sous le seuil.',
        'reports.report_success': '✅ Rapport généré avec succès',
        'reports.no_reports_yet': 'Aucun rapport généré pour le moment.',

        'users.title': 'UTILISATEURS',
        'users.add_user': 'Ajouter un utilisateur',
        'users.username': "Nom d'utilisateur:",
        'users.full_name': 'Nom complet:',
        'users.password': 'Mot de passe:',
        'users.confirm': 'Confirmer:',
        'users.role': 'Rôle:',
        'users.role_cashier': 'Caissier',
        'users.role_owner': 'Propriétaire',
        'users.create': 'Créer',
        'users.col_id': 'ID',
        'users.col_username': 'Utilisateur',
        'users.col_full_name': 'Nom complet',
        'users.col_role': 'Rôle',
        'users.col_active': 'Actif',
        'users.col_created': 'Créé le',
        'users.rename': 'Renommer',
        'users.toggle_active': 'Activer / Désactiver',
        'users.change_password': 'Changer mot de passe',
        'users.delete': 'Supprimer',
        'users.warn_owner': '⚠️ Ne pas supprimer le compte propriétaire.',
        'users.required_fields': "Nom d'utilisateur et mot de passe requis",
        'users.password_mismatch': 'Les mots de passe ne correspondent pas',
        'users.password_short': 'Mot de passe trop court (min 4 caractères)',
        'users.created_ok': "Utilisateur '{u}' créé",
        'users.select_user': 'Sélectionnez un utilisateur',
        'users.rename_title': 'Renommer - {u}',
        'users.new_name_for': "Nouveau nom pour '{u}':",
        'users.name_empty': 'Le nom ne peut pas être vide',
        'users.renamed_ok': "Renommé en '{u}'",
        'users.cannot_disable_self': 'Vous ne pouvez pas désactiver votre propre compte',
        'users.cannot_delete_self': 'Vous ne pouvez pas supprimer votre propre compte',
        'users.confirm_delete': "Supprimer l'utilisateur '{u}' ?",
        'users.password_new': 'Nouveau mot de passe:',
        'users.password_changed': 'Mot de passe modifié',
        'users.active_yes': 'Oui',
        'users.active_no': 'Non',

        'startup.no_screen': 'Aucun écran accessible pour ce rôle.',
        'startup.permission_denied': "Vous n'avez pas la permission d'ouvrir cet écran.",
    },

    # =====================================================================
    # العربية
    # =====================================================================
    'ar': {
        'app.title': 'إدارة المخزون',
        'app.window_title': 'إدارة المخزون — {username} ({role})',
        'nav.sales': 'المبيعات',
        'nav.products': 'المنتجات',
        'nav.history': 'السجل',
        'nav.reports': 'التقارير',
        'nav.users': 'المستخدمون',
        'nav.deleted': 'المهملات',
        'nav.back_to_sales': 'المبيعات →',
        'nav.back_to_products': 'المنتجات →',
        'nav.back_to_history': 'السجل →',
        'nav.reports_arrow': '← التقارير',
        'nav.users_arrow': '← المستخدمون',
        'nav.products_arrow': '← المنتجات',
        'nav.sales_arrow': '← المبيعات',

        'role.owner': 'المالك',
        'role.cashier': 'أمين الصندوق',

        'login.title': 'تسجيل الدخول',
        'login.subtitle': 'الرجاء تسجيل الدخول',
        'login.username': 'اسم المستخدم:',
        'login.password': 'كلمة المرور:',
        'login.connect': 'دخول',
        'login.language': 'اللغة:',
        'login.error_empty': 'الرجاء إدخال بيانات الاعتماد',
        'login.error_invalid': 'بيانات اعتماد غير صالحة',

        'btn.add': 'إضافة',
        'btn.modify': 'تعديل',
        'btn.clear': 'مسح',
        'btn.delete': 'حذف',
        'btn.cancel': 'إلغاء',
        'btn.close': 'إغلاق',
        'btn.save': 'حفظ',
        'btn.filter': 'تصفية',
        'btn.clear_filter': 'مسح التصفية',
        'btn.refresh': '↻',
        'btn.verify': '🔍 تحقق',
        'btn.details': 'تفاصيل',
        'btn.details_sale': 'تفاصيل البيع',
        'btn.choose_photo': 'اختيار صورة',
        'btn.add_stock': 'إضافة مخزون',
        'btn.delete_selection': 'حذف المحدد',
        'btn.ok': 'موافق',
        'btn.yes': 'نعم',
        'btn.no': 'لا',

        'lbl.total': 'الإجمالي',
        'lbl.profit': 'الربح',
        'lbl.sales_count': 'المبيعات',
        'lbl.date': 'التاريخ',
        'lbl.time': 'الوقت',
        'lbl.quantity': 'الكمية',
        'lbl.unit': 'الوحدة',
        'lbl.article': 'العنصر',
        'lbl.articles': 'العناصر',
        'lbl.product': 'المنتج',
        'lbl.products': 'المنتجات',
        'lbl.from': 'من:',
        'lbl.to': 'إلى:',
        'lbl.period': 'الفترة',
        'lbl.by': 'بواسطة',

        'unit.piece': 'قطعة',
        'unit.gram': 'غرام',
        'unit.pack': 'علبة',
        'unit.cigarette': 'سيجارة',
        'unit.pieces': 'قطعة',
        'unit.packs_short': 'علبة',
        'unit.pieces_short': 'قطعة',
        'unit.units': 'وحدة',
        'unit.unit_price': 'سعر الوحدة:',

        'msg.success': 'نجاح',
        'msg.error': 'خطأ',
        'msg.warning': 'تنبيه',
        'msg.info': 'معلومة',
        'msg.confirmation': 'تأكيد',
        'msg.access_denied': 'تم رفض الوصول',
        'msg.no_permission': 'تم رفض الإذن.',
        'msg.invalid_numbers': 'الرجاء إدخال أرقام صحيحة',
        'msg.stock_insufficient': 'المخزون غير كافٍ! المتوفر: {available}',
        'msg.stock_only': 'المخزون: {stock} فقط!',

        'sales.title': 'المبيعات',
        'sales.scanner_search': 'ماسح / بحث',
        'sales.hint_scan': '📷 أرقام = مسح',
        'sales.hint_search': '🔍 حروف = بحث',
        'sales.telecom': 'الاتصالات',
        'sales.telecom_shortcuts': 'الاتصالات  [F1 – F6]',
        'sales.cart': 'السلة',
        'sales.cart_pay_hint': '[مسافة] = دفع',
        'sales.btn_remove': 'إزالة',
        'sales.btn_clear': 'تفريغ',
        'sales.btn_pay': '[مسافة] دفع',
        'sales.state_scan': '📷 مسح — F1-F6=اتصالات | حروف=بحث | مسافة=دفع',
        'sales.state_searching': '🔍 بحث — ↑↓ تنقل | إدخال اختيار',
        'sales.state_popup': '🪟 نافذة — الكمية | U=وحدة | إدخال=موافق | ESC=إغلاق',
        'sales.shortcuts_bar': ' [F1-F6] اتصالات • [مسافة] دفع • [ESC] إلغاء',
        'sales.not_found': 'غير موجود',
        'sales.cart_empty': 'السلة فارغة',
        'sales.added': 'تمت الإضافة {name}',
        'sales.added_qty': 'تمت الإضافة {qty:g} {unit}',
        'sales.cash_in': 'تم الدفع: {total:.2f} د.ت',
        'sales.save_error': 'تعذر حفظ البيع:\n{e}',
        'sales.popup_weight_title': 'منتج بالوزن',
        'sales.popup_pack_title': 'منتج بالعلبة',
        'sales.popup_cigarette_title': 'السيجارة',
        'sales.price': 'السعر',
        'sales.price_per_kg': 'السعر: {p:.2f} د.ت/كغ',
        'sales.pack_price': 'سعر العلبة : {p:.2f} د.ت',
        'sales.unit_price': 'سعر الوحدة: {p:.2f} د.ت',
        'sales.stock_cigarettes': 'المخزون: {n} سيجارة',
        'sales.sell_in': 'البيع بـ:',
        'sales.opt_packs': 'علب',
        'sales.opt_units': 'وحدات',
        'sales.opt_grams': 'غرام (غ)',
        'sales.opt_kilograms': 'كيلوغرام (كغ)',
        'sales.qty': 'الكمية:',
        'sales.popup_hint': '[U] تغيير الوحدة   •   [Enter] إضافة   •   [ESC] إلغاء',
        'sales.not_found_full': 'غير موجود: {name}',

        'products.title': 'المنتجات',
        'products.add_modify': 'إضافة / تعديل',
        'products.barcode': 'الباركود:',
        'products.name': 'الاسم:',
        'products.buy_price': 'سعر الشراء:',
        'products.sell_price': 'سعر البيع:',
        'products.stock': 'المخزون:',
        'products.unit_label': 'الوحدة:',
        'products.unit_piece': 'قطعة',
        'products.unit_gram': 'غرام',
        'products.unit_pack': 'علبة',
        'products.unit_cigarette': 'سيجارة',
        'products.single_price': 'سعر الوحدة:',
        'products.pieces_per_pack': 'قطع/علبة:',
        'products.cigarette_price': 'سعر السيجارة:',
        'products.cig_stock_hint': 'المخزون بالسيجارات الفردية\n(مثال: 2000 = 100 علبة)',
        'products.no_photo': 'لا توجد صورة محددة',
        'products.search': 'بحث:',
        'products.col_id': 'المعرف',
        'products.col_barcode': 'الباركود',
        'products.col_name': 'الاسم',
        'products.col_buy': 'الشراء',
        'products.col_sell': 'البيع',
        'products.col_unit': 'الوحدة',
        'products.col_stock': 'المخزون',
        'products.col_type': 'النوع',
        'products.success_added': 'تمت إضافة المنتج!',
        'products.success_updated': 'تم تعديل المنتج!',
        'products.confirm_delete': 'حذف هذا المنتج؟',
        'products.select_first': 'اختر منتجاً أولاً',
        'products.name_required': 'اسم المنتج مطلوب',
        'products.sell_gt_buy': 'سعر البيع يجب أن يكون أكبر من سعر الشراء',
        'products.pieces_gt_zero': 'قطع/علبة يجب أن يكون أكبر من 0',
        'products.add_stock_title': 'إضافة إلى المخزون',
        'products.current_stock_pack': 'المخزون الحالي: {packs} علبة + {pieces} قطعة',
        'products.current_stock_cig': 'المخزون الحالي: {packs} علبة + {units} وحدة',
        'products.current_stock_g': 'المخزون الحالي: {stock} غ',
        'products.current_stock': 'المخزون الحالي: {stock}',
        'products.add_packs': 'إضافة علب:',
        'products.add_pieces': 'إضافة قطع:',
        'products.add_cig': 'إضافة بالسيجارات الفردية:',
        'products.add_cig_hint': '(مثال: 20 = علبة واحدة)',
        'products.add_g': 'إضافة غرامات:',
        'products.qty_to_add': 'الكمية للإضافة:',
        'products.positive_number': 'الرجاء إدخال رقم موجب',
        'products.stock_added': 'تمت إضافة المخزون',
        'products.owner_only': 'المالك فقط يمكنه إدارة المنتجات.',

        'history.title': 'السجل',
        'history.deleted_btn': '🗑️ المهملات',
        'history.col_date': 'التاريخ',
        'history.col_time': 'الوقت',
        'history.col_count': 'العناصر',
        'history.col_total': 'الإجمالي (د.ت)',
        'history.col_profit': 'الربح (د.ت)',
        'history.btn_soft_delete': 'حذف (مؤقت)',
        'history.btn_hard_delete': 'حذف نهائي',
        'history.hint': '⚠️ مؤقت = مخفي + استرجاع المخزون • نهائي = لا رجعة فيه',
        'history.select_to_delete': 'اختر عملية بيع واحدة أو أكثر للحذف',
        'history.confirm_soft': 'حذف {n} عملية بيع؟\nسيتم إخفاء البيع واسترجاع المخزون.',
        'history.confirm_hard': 'حذف نهائي لـ {n} عملية بيع؟\nهذا الإجراء لا رجعة فيه.',
        'history.deleted_ok': 'تم حذف {n} عملية بيع',
        'history.owner_only_hard': 'المالك فقط يمكنه الحذف النهائي.',
        'history.select_sale': 'اختر عملية بيع',
        'history.no_items': 'لم يبقَ عناصر في هذه العملية.',
        'history.details_title': 'التفاصيل - {ts}',
        'history.sale_of': 'بيع بتاريخ {ts}',
        'history.col_id': 'المعرف',
        'history.col_product': 'المنتج',
        'history.col_qty': 'الكمية',
        'history.col_unit': 'الوحدة',
        'history.delete_item': 'حذف العنصر المحدد',
        'history.delete_item_confirm': 'حذف هذا العنصر؟ سيتم استرجاع المخزون.',
        'history.delete_item_confirm_hard': 'حذف نهائي لهذا العنصر؟\nلا رجعة فيه.',
        'history.verify_total': 'الإجمالي الفعلي للمبيعات : {t:.2f} د.ت',
        'history.verify_grouped': 'الإجمالي المجمع        : {t:.2f} د.ت',
        'history.verify_profit': 'الربح الفعلي            : {p:.2f} د.ت',
        'history.verify_grouped_profit': 'الربح المجمع            : {p:.2f} د.ت',
        'history.verify_ok': '✅ متوافق',
        'history.verify_bad': '⚠️ تم اكتشاف عدم اتساق!',
        'history.verify_title': 'التحقق',

        'deleted.title': 'المهملات — المبيعات المحذوفة',
        'deleted.deleted_from': 'محذوف من:',
        'deleted.to': 'إلى:',
        'deleted.filter': 'تصفية',
        'deleted.view_all': 'عرض الكل',
        'deleted.col_deleted_at': 'حُذف في',
        'deleted.col_time': 'الوقت',
        'deleted.col_by': 'بواسطة',
        'deleted.col_items': 'العناصر',
        'deleted.col_total': 'الإجمالي (د.ت)',
        'deleted.col_profit': 'الربح (د.ت)',
        'deleted.restore_selection': 'استرجاع المحدد',
        'deleted.select_to_restore': 'اختر مدخلاً أو أكثر للاسترجاع',
        'deleted.confirm_restore': 'استرجاع {n} مجموعة من المبيعات المحذوفة؟\nستعود المبيعات إلى السجل وسيتم تعديل المخزون.',
        'deleted.restore_ok': 'تم استرجاع {n} مجموعة',
        'deleted.details_title': 'مبيعات محذوفة في {ts}',
        'deleted.deleted_on': 'محذوف في {ts}',
        'deleted.col_sale_of': 'بيع بتاريخ',
        'deleted.col_reason': 'السبب',
        'deleted.restore_one': 'استرجاع العنصر المحدد',
        'deleted.confirm_restore_one': 'استرجاع هذا العنصر؟\nسيعود إلى السجل وسيتم تعديل المخزون.',
        'deleted.nothing_to_show': 'لا شيء لعرضه لهذا المدخل.',
        'deleted.no_more_items': 'لا مزيد من العناصر لهذا المدخل.',
        'deleted.select_item': 'اختر عنصراً',
        'deleted.unknown_user': '(غير معروف)',

        'reports.title': 'التقارير',
        'reports.tab_summary': '📊 ملخص المبيعات',
        'reports.tab_products': '🏆 أفضل المنتجات',
        'reports.tab_stock': '📦 حالة المخزون',
        'reports.tab_export': '📄 تصدير التقرير',
        'reports.period': 'الفترة',
        'reports.load_summary': 'تحميل الملخص',
        'reports.today': 'اليوم',
        'reports.summary_header': 'ملخص من {start} إلى {end}',
        'reports.total_sales': 'إجمالي المبيعات',
        'reports.total_profit': 'إجمالي الربح',
        'reports.transactions': 'العمليات',
        'reports.period_optional': 'الفترة (اختياري)',
        'reports.num_products': 'عدد المنتجات:',
        'reports.load_top': 'تحميل أفضل المنتجات',
        'reports.clear_period': 'مسح الفترة',
        'reports.col_product': 'المنتج',
        'reports.col_qty': 'الكمية',
        'reports.col_revenue': 'الإيرادات (د.ت)',
        'reports.col_profit': 'الربح (د.ت)',
        'reports.low_stock_threshold': 'عتبة المخزون المنخفض:',
        'reports.refresh_btn': 'تحديث',
        'reports.stock_value': 'القيمة الإجمالية للمخزون (سعر الشراء) : {v:.2f} د.ت',
        'reports.low_stock_header': '⚠️  المنتجات ذات المخزون المنخفض (عتبة {t}) :',
        'reports.no_low_stock': '  لا يوجد',
        'reports.report_period': 'فترة التقرير',
        'reports.generate': '📄 إنشاء التقرير',
        'reports.from_last': '⏪ منذ التقرير الأخير',
        'reports.open_folder': '📁 فتح المجلد',
        'reports.preview': 'معاينة',
        'reports.invalid_datetime': 'صيغة التاريخ/الوقت غير صحيحة.',
        'reports.start_after_end': 'تاريخ البداية بعد تاريخ النهاية.',
        'reports.no_previous': 'لا يوجد تقرير سابق.',
        'reports.corrupt_last': 'ملف التقرير الأخير تالف.',
        'reports.cannot_open': 'تعذر فتح المجلد:\n{e}',
        'reports.cannot_write': 'تعذر كتابة التقرير:\n{e}',
        'reports.report_saved': 'تم حفظ التقرير في:\n{path}',
        'reports.report_title': '📋 تقرير الفترة',
        'reports.report_from': 'من : {d}',
        'reports.report_to': 'إلى : {d}',
        'reports.report_generated': 'أُنشئ في : {d}',
        'reports.report_by': 'بواسطة : {u}',
        'reports.report_sales_summary': '📊 ملخص المبيعات',
        'reports.report_total_sales': 'إجمالي المبيعات     : {v:>12.2f} د.ت',
        'reports.report_total_profit': 'إجمالي الربح       : {v:>12.2f} د.ت',
        'reports.report_num_trans': 'عدد العمليات : {n:>10}',
        'reports.report_top10': '🏆 أفضل 10 منتجات',
        'reports.report_no_sales': '  لا مبيعات في هذه الفترة.',
        'reports.report_stock': '📦 حالة المخزون',
        'reports.report_stock_value': 'القيمة الإجمالية للمخزون : {v:.2f} د.ت',
        'reports.report_low_stock': '⚠️  المنتجات ذات المخزون المنخفض (عتبة {t})',
        'reports.report_none': '  لا يوجد',
        'reports.report_hidden': '  ... و {n} منتج/منتجات أخرى تحت العتبة.',
        'reports.report_success': '✅ تم إنشاء التقرير بنجاح',
        'reports.no_reports_yet': 'لم يتم إنشاء أي تقرير بعد.',

        'users.title': 'المستخدمون',
        'users.add_user': 'إضافة مستخدم',
        'users.username': 'اسم المستخدم:',
        'users.full_name': 'الاسم الكامل:',
        'users.password': 'كلمة المرور:',
        'users.confirm': 'تأكيد:',
        'users.role': 'الدور:',
        'users.role_cashier': 'أمين صندوق',
        'users.role_owner': 'مالك',
        'users.create': 'إنشاء',
        'users.col_id': 'المعرف',
        'users.col_username': 'اسم المستخدم',
        'users.col_full_name': 'الاسم الكامل',
        'users.col_role': 'الدور',
        'users.col_active': 'نشط',
        'users.col_created': 'أُنشئ في',
        'users.rename': 'إعادة تسمية',
        'users.toggle_active': 'تنشيط / إلغاء تنشيط',
        'users.change_password': 'تغيير كلمة المرور',
        'users.delete': 'حذف',
        'users.warn_owner': '⚠️ لا تحذف حساب المالك.',
        'users.required_fields': 'اسم المستخدم وكلمة المرور مطلوبان',
        'users.password_mismatch': 'كلمتا المرور غير متطابقتين',
        'users.password_short': 'كلمة المرور قصيرة جداً (4 أحرف على الأقل)',
        'users.created_ok': "تم إنشاء المستخدم '{u}'",
        'users.select_user': 'اختر مستخدماً',
        'users.rename_title': 'إعادة تسمية - {u}',
        'users.new_name_for': "الاسم الجديد لـ '{u}':",
        'users.name_empty': 'لا يمكن أن يكون الاسم فارغاً',
        'users.renamed_ok': "أُعيد التسمية إلى '{u}'",
        'users.cannot_disable_self': 'لا يمكنك تعطيل حسابك الخاص',
        'users.cannot_delete_self': 'لا يمكنك حذف حسابك الخاص',
        'users.confirm_delete': "حذف المستخدم '{u}'؟",
        'users.password_new': 'كلمة المرور الجديدة:',
        'users.password_changed': 'تم تغيير كلمة المرور',
        'users.active_yes': 'نعم',
        'users.active_no': 'لا',

        'startup.no_screen': 'لا يوجد شاشة متاحة لهذا الدور.',
        'startup.permission_denied': 'ليس لديك إذن لفتح هذه الشاشة.',
    },
}


# ---------------------------------------------------------------------------
# RTL helpers — these MUST be used everywhere in screens
# ---------------------------------------------------------------------------
def is_rtl() -> bool:
    """True if current language is right-to-left."""
    return _current in RTL_LANGUAGES


def side_start() -> str:
    """'start' side of reading order (right in RTL, left in LTR)."""
    return 'right' if is_rtl() else 'left'


def side_end() -> str:
    """'end' side of reading order (left in RTL, right in LTR)."""
    return 'left' if is_rtl() else 'right'


def anchor_start() -> str:
    """Text anchor at start of reading (e in RTL, w in LTR)."""
    return 'e' if is_rtl() else 'w'


def anchor_end() -> str:
    """Text anchor at end of reading (w in RTL, e in LTR)."""
    return 'w' if is_rtl() else 'e'


def justify_text() -> str:
    """Justification for Entry/Text widgets."""
    return 'right' if is_rtl() else 'left'


# ---------------------------------------------------------------------------
# Font selection
#
# Tk does NOT shape Arabic by itself — it relies on the platform text engine.
# If the chosen family has no Arabic glyphs, Tk renders Arabic as isolated,
# LTR-ordered letters. So we probe which families Tk actually has installed
# and pick the first one that can shape Arabic.
# ---------------------------------------------------------------------------
_ARABIC_FONTS = (
    "Noto Naskh Arabic",     # best shaping, common on Linux
    "Noto Sans Arabic",      # Linux
    "Noto Sans",             # Linux, includes Arabic since 2.x
    "DejaVu Sans",           # ships with nearly every distro, has Arabic
    "FreeSans",              # GNU FreeFont
    "Tahoma",                # Windows
    "Segoe UI",              # Windows
    "Geeza Pro",             # macOS
    "Arial Unicode MS",      # macOS / older Windows
    "Arial",                 # last resort
)

_LATIN_FONTS = (
    "Helvetica",
    "DejaVu Sans",
    "Arial",
)


def _pick_font(candidates):
    """Return the first family in `candidates` that Tk knows about."""
    try:
        import tkinter.font as tkfont
        available = set(tkfont.families())
    except Exception:
        return candidates[0] if candidates else "TkDefaultFont"
    for family in candidates:
        if family in available:
            return family
    return candidates[-1] if candidates else "TkDefaultFont"


def ui_font(size: int, weight: str = "normal"):
    """Return a tuple usable as a font spec, with an Arabic-friendly fallback."""
    family = _pick_font(_ARABIC_FONTS if is_rtl() else _LATIN_FONTS)
    if weight and weight != "normal":
        return (family, size, weight)
    return (family, size)


# ---------------------------------------------------------------------------
# Arabic pre-shaping for Tk
#
# Two things must happen before Tk sees an Arabic string on Linux:
#   1. Contextual shaping: each Arabic letter must be replaced by the correct
#      isolated / initial / medial / final presentation form, depending on its
#      neighbours.
#   2. Bidi reordering: mixed Arabic + Latin + digits must be reordered into
#      visual (left-to-right) order because Tk renders strictly left-to-right.
# We do both here. The transformation is a no-op for non-Arabic strings and
# for languages that are not RTL.
# ---------------------------------------------------------------------------
def _has_arabic(text: str) -> bool:
    for ch in text:
        # Arabic block + Arabic Supplement + Arabic Presentation Forms
        if ('\u0600' <= ch <= '\u06FF' or
                '\u0750' <= ch <= '\u077F' or
                '\uFB50' <= ch <= '\uFDFF' or
                '\uFE70' <= ch <= '\uFEFF'):
            return True
    return False


def rtl_display(text):
    """
    Convert a logical-order string into the visual-order, pre-shaped string
    that Tk on Linux needs in order to show Arabic correctly.

    Safe to call on any string; it only modifies text that contains Arabic
    characters, and only when the libraries are installed.
    """
    if not text or not isinstance(text, str):
        return text
    if not _HAS_ARABIC_SHAPING:
        return text
    if not _has_arabic(text):
        return text
    try:
        return _bidi_display(arabic_reshaper.reshape(text))
    except Exception:
        # Never let a shaping error take down the UI
        return text


# ---------------------------------------------------------------------------
# Config / translation
# ---------------------------------------------------------------------------
def _load_config():
    global _current
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                lang = data.get('language', 'fr')
                if lang in LANGUAGES:
                    _current = lang
        except Exception:
            pass
    return _current


def save_config(lang):
    global _current
    if lang not in LANGUAGES:
        return
    _current = lang
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump({'language': lang}, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def get_language():
    return _current


def set_language(lang):
    save_config(lang)


def t(key, **kwargs):
    """
    Translate a key. Falls back to English, then to the key itself.

    The returned string has already been pre-shaped and bidi-reordered for
    Tk, so screens can drop it straight into a Label/Button/Entry without
    any further processing.
    """
    d = TRANSLATIONS.get(_current, {})
    text = d.get(key)
    if text is None:
        text = TRANSLATIONS['en'].get(key, key)
    if kwargs:
        try:
            text = text.format(**kwargs)
        except Exception:
            pass
    return rtl_display(text)


_load_config()
