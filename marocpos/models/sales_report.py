from database import get_connection
from datetime import datetime, timedelta
import json
import sqlite3

class SalesReport:
    """Class to generate and manage sales reports"""
    
    @staticmethod
    def get_daily_sales(date=None):
        """Get sales data for a specific date, defaults to today"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
            
        conn = get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                
                # Format the date strings for comparison
                start_date = f"{date} 00:00:00"
                end_date = f"{date} 23:59:59"
                
                # Get total sales data
                cursor.execute("""
                    SELECT 
                        COUNT(*) as sale_count,
                        SUM(final_total) as total_sales,
                        AVG(final_total) as average_sale,
                        MIN(final_total) as min_sale,
                        MAX(final_total) as max_sale,
                        SUM(discount) as total_discount
                    FROM Sales
                    WHERE created_at BETWEEN ? AND ?
                """, (start_date, end_date))
                
                summary = dict(cursor.fetchone() or {})
                
                # Get all sales for the day with details
                cursor.execute("""
                    SELECT 
                        s.id, 
                        s.created_at, 
                        COALESCE(u.username, 'Inconnu') as username,
                        COUNT(si.id) as item_count,
                        s.total_amount, 
                        s.discount, 
                        s.final_total
                    FROM Sales s
                    LEFT JOIN Users u ON s.user_id = u.id
                    LEFT JOIN SaleItems si ON s.id = si.sale_id
                    WHERE s.created_at BETWEEN ? AND ?
                    GROUP BY s.id
                    ORDER BY s.created_at
                """, (start_date, end_date))
                
                sales = [dict(row) for row in cursor.fetchall()]
                
                # Get sales by hour
                cursor.execute("""
                    SELECT 
                        strftime('%H', created_at) as hour,
                        COUNT(*) as sale_count,
                        SUM(final_total) as total_sales
                    FROM Sales
                    WHERE created_at BETWEEN ? AND ?
                    GROUP BY hour
                    ORDER BY hour
                """, (start_date, end_date))
                
                hourly_sales = [dict(row) for row in cursor.fetchall()]
                
                # Get sales by payment method
                cursor.execute("""
                    SELECT 
                        COALESCE(pm.name, s.payment_method) as payment_method,
                        COUNT(DISTINCT s.id) as transaction_count,
                        SUM(COALESCE(sp.amount, s.final_total)) as total_amount
                    FROM Sales s
                    LEFT JOIN SalePayments sp ON s.id = sp.sale_id
                    LEFT JOIN PaymentMethods pm ON sp.payment_method_id = pm.id
                    WHERE s.created_at BETWEEN ? AND ?
                    GROUP BY payment_method
                    ORDER BY total_amount DESC
                """, (start_date, end_date))
                
                payment_methods = [dict(row) for row in cursor.fetchall()]
                
                # Top selling products
                cursor.execute("""
                    SELECT 
                        p.id as product_id,
                        p.name as product_name,
                        SUM(si.quantity) as quantity_sold,
                        SUM(si.subtotal) as total_sales,
                        COUNT(DISTINCT s.id) as number_of_sales
                    FROM SaleItems si
                    JOIN Sales s ON si.sale_id = s.id
                    JOIN Products p ON si.product_id = p.id
                    WHERE s.created_at BETWEEN ? AND ?
                    GROUP BY p.id
                    ORDER BY quantity_sold DESC
                    LIMIT 10
                """, (start_date, end_date))
                
                top_products = [dict(row) for row in cursor.fetchall()]
                
                # Top selling categories
                cursor.execute("""
                    SELECT 
                        COALESCE(c.name, 'Non catégorisé') as category_name,
                        COUNT(DISTINCT si.id) as items_sold,
                        SUM(si.subtotal) as total_sales
                    FROM SaleItems si
                    JOIN Sales s ON si.sale_id = s.id
                    JOIN Products p ON si.product_id = p.id
                    LEFT JOIN Categories c ON p.category_id = c.id
                    WHERE s.created_at BETWEEN ? AND ?
                    GROUP BY COALESCE(c.name, 'Non catégorisé')
                    ORDER BY total_sales DESC
                """, (start_date, end_date))
                
                top_categories = [dict(row) for row in cursor.fetchall()]
                
                result = {
                    'date': date,
                    'summary': summary,
                    'sales': sales,
                    'hourly_sales': hourly_sales,
                    'payment_methods': payment_methods,
                    'top_products': top_products,
                    'top_categories': top_categories
                }
                
                return result
            except Exception as e:
                print(f"Error getting daily sales: {e}")
                return None
            finally:
                conn.close()
        return None
    
    @staticmethod
    def get_sales_range(start_date, end_date):
        """Get sales data for a date range"""
        conn = get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                
                # Format the date strings for comparison if they're not already formatted
                if not start_date.endswith('00:00:00'):
                    start_date = f"{start_date} 00:00:00"
                if not end_date.endswith('23:59:59'):
                    end_date = f"{end_date} 23:59:59"
                
                # Get total sales data
                cursor.execute("""
                    SELECT 
                        COUNT(*) as sale_count,
                        SUM(final_total) as total_sales,
                        AVG(final_total) as average_sale,
                        MIN(final_total) as min_sale,
                        MAX(final_total) as max_sale,
                        SUM(discount) as total_discount
                    FROM Sales
                    WHERE created_at BETWEEN ? AND ?
                """, (start_date, end_date))
                
                summary = dict(cursor.fetchone() or {})
                
                # Get sales by day
                cursor.execute("""
                    SELECT 
                        date(created_at) as day,
                        COUNT(*) as sale_count,
                        SUM(final_total) as total_sales
                    FROM Sales
                    WHERE created_at BETWEEN ? AND ?
                    GROUP BY day
                    ORDER BY day
                """, (start_date, end_date))
                
                daily_sales = [dict(row) for row in cursor.fetchall()]
                
                # Get sales by payment method
                cursor.execute("""
                    SELECT 
                        COALESCE(pm.name, s.payment_method) as payment_method,
                        COUNT(DISTINCT s.id) as transaction_count,
                        SUM(COALESCE(sp.amount, s.final_total)) as total_amount
                    FROM Sales s
                    LEFT JOIN SalePayments sp ON s.id = sp.sale_id
                    LEFT JOIN PaymentMethods pm ON sp.payment_method_id = pm.id
                    WHERE s.created_at BETWEEN ? AND ?
                    GROUP BY payment_method
                    ORDER BY total_amount DESC
                """, (start_date, end_date))
                
                payment_methods = [dict(row) for row in cursor.fetchall()]
                
                # Top selling products
                cursor.execute("""
                    SELECT 
                        p.id as product_id,
                        p.name as product_name,
                        SUM(si.quantity) as quantity_sold,
                        SUM(si.subtotal) as total_sales,
                        COUNT(DISTINCT s.id) as number_of_sales
                    FROM SaleItems si
                    JOIN Sales s ON si.sale_id = s.id
                    JOIN Products p ON si.product_id = p.id
                    WHERE s.created_at BETWEEN ? AND ?
                    GROUP BY p.id
                    ORDER BY quantity_sold DESC
                    LIMIT 20
                """, (start_date, end_date))
                
                top_products = [dict(row) for row in cursor.fetchall()]
                
                # Top selling categories
                cursor.execute("""
                    SELECT 
                        COALESCE(c.name, 'Non catégorisé') as category_name,
                        COUNT(DISTINCT si.id) as items_sold,
                        SUM(si.subtotal) as total_sales
                    FROM SaleItems si
                    JOIN Sales s ON si.sale_id = s.id
                    JOIN Products p ON si.product_id = p.id
                    LEFT JOIN Categories c ON p.category_id = c.id
                    WHERE s.created_at BETWEEN ? AND ?
                    GROUP BY COALESCE(c.name, 'Non catégorisé')
                    ORDER BY total_sales DESC
                """, (start_date, end_date))
                
                top_categories = [dict(row) for row in cursor.fetchall()]
                
                # Get sales by user
                cursor.execute("""
                    SELECT 
                        u.username as user,
                        COUNT(s.id) as sale_count,
                        SUM(s.final_total) as total_sales
                    FROM Sales s
                    JOIN Users u ON s.user_id = u.id
                    WHERE s.created_at BETWEEN ? AND ?
                    GROUP BY u.username
                    ORDER BY total_sales DESC
                """, (start_date, end_date))
                
                sales_by_user = [dict(row) for row in cursor.fetchall()]
                
                result = {
                    'start_date': start_date.split()[0],
                    'end_date': end_date.split()[0],
                    'summary': summary,
                    'daily_sales': daily_sales,
                    'payment_methods': payment_methods,
                    'top_products': top_products,
                    'top_categories': top_categories,
                    'sales_by_user': sales_by_user
                }
                
                return result
            except Exception as e:
                print(f"Error getting sales range: {e}")
                return None
            finally:
                conn.close()
        return None
    
    @staticmethod
    def get_product_performance(product_id, start_date=None, end_date=None):
        """Get sales performance data for a specific product"""
        conn = get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                
                query = """
                    SELECT 
                        p.id as product_id,
                        p.name as product_name,
                        p.unit_price as current_price,
                        p.purchase_price as current_cost,
                        SUM(si.quantity) as total_quantity,
                        SUM(si.subtotal) as total_sales,
                        COUNT(DISTINCT s.id) as number_of_sales,
                        AVG(si.unit_price) as average_price,
                        date(MIN(s.created_at)) as first_sold,
                        date(MAX(s.created_at)) as last_sold
                    FROM SaleItems si
                    JOIN Sales s ON si.sale_id = s.id
                    JOIN Products p ON si.product_id = p.id
                    WHERE si.product_id = ?
                """
                
                params = [product_id]
                
                if start_date:
                    query += " AND s.created_at >= ?"
                    params.append(f"{start_date} 00:00:00")
                    
                if end_date:
                    query += " AND s.created_at <= ?"
                    params.append(f"{end_date} 23:59:59")
                    
                query += " GROUP BY p.id"
                
                cursor.execute(query, params)
                product_summary = dict(cursor.fetchone() or {})
                
                # Get sales by month
                query = """
                    SELECT 
                        strftime('%Y-%m', s.created_at) as month,
                        SUM(si.quantity) as quantity_sold,
                        SUM(si.subtotal) as total_sales,
                        COUNT(DISTINCT s.id) as number_of_sales
                    FROM SaleItems si
                    JOIN Sales s ON si.sale_id = s.id
                    WHERE si.product_id = ?
                """
                
                params = [product_id]
                
                if start_date:
                    query += " AND s.created_at >= ?"
                    params.append(f"{start_date} 00:00:00")
                    
                if end_date:
                    query += " AND s.created_at <= ?"
                    params.append(f"{end_date} 23:59:59")
                    
                query += " GROUP BY month ORDER BY month"
                
                cursor.execute(query, params)
                monthly_sales = [dict(row) for row in cursor.fetchall()]
                
                # Get variant sales if product has variants
                cursor.execute("""
                    SELECT has_variants FROM Products WHERE id = ?
                """, (product_id,))
                
                has_variants = cursor.fetchone()
                variant_sales = []
                
                if has_variants and has_variants.get('has_variants', 0):
                    query = """
                        SELECT 
                            si.variant_id,
                            pv.attribute_values,
                            SUM(si.quantity) as quantity_sold,
                            SUM(si.subtotal) as total_sales,
                            COUNT(DISTINCT s.id) as number_of_sales
                        FROM SaleItems si
                        JOIN Sales s ON si.sale_id = s.id
                        JOIN ProductVariants pv ON si.variant_id = pv.id
                        WHERE si.product_id = ? AND si.variant_id IS NOT NULL
                    """
                    
                    params = [product_id]
                    
                    if start_date:
                        query += " AND s.created_at >= ?"
                        params.append(f"{start_date} 00:00:00")
                        
                    if end_date:
                        query += " AND s.created_at <= ?"
                        params.append(f"{end_date} 23:59:59")
                        
                    query += " GROUP BY si.variant_id ORDER BY quantity_sold DESC"
                    
                    cursor.execute(query, params)
                    variant_rows = cursor.fetchall()
                    
                    for row in variant_rows:
                        variant_data = dict(row)
                        
                        # Parse attribute_values
                        try:
                            if variant_data.get('attribute_values'):
                                if isinstance(variant_data['attribute_values'], str):
                                    variant_data['attributes'] = json.loads(variant_data['attribute_values'])
                                else:
                                    variant_data['attributes'] = variant_data['attribute_values']
                                    
                                # Create a display name for the variant
                                if isinstance(variant_data['attributes'], dict):
                                    variant_data['variant_name'] = " / ".join(str(v) for v in variant_data['attributes'].values() if v)
                                else:
                                    variant_data['variant_name'] = f"Variant #{variant_data.get('variant_id', '')}"
                        except:
                            variant_data['attributes'] = {}
                            variant_data['variant_name'] = f"Variant #{variant_data.get('variant_id', '')}"
                            
                        variant_sales.append(variant_data)
                
                return {
                    'product': product_summary,
                    'monthly_sales': monthly_sales,
                    'variant_sales': variant_sales
                }
            except Exception as e:
                print(f"Error getting product performance: {e}")
                return None
            finally:
                conn.close()
        return None
    
    @staticmethod
    def get_inventory_report():
        """Get inventory status report for all products"""
        conn = get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                
                # Get inventory status for regular products
                cursor.execute("""
                    SELECT 
                        p.id as product_id,
                        p.name as product_name,
                        COALESCE(c.name, 'Non catégorisé') as category_name,
                        p.stock as current_stock,
                        p.min_stock as minimum_stock,
                        p.reorder_point as reorder_point,
                        p.purchase_price as cost,
                        p.unit_price as price,
                        p.has_variants,
                        CASE 
                            WHEN p.stock <= p.min_stock THEN 'low'
                            WHEN p.stock <= p.reorder_point THEN 'warning'
                            ELSE 'ok'
                        END as stock_status,
                        p.purchase_price * p.stock as stock_value,
                        p.unit_price * p.stock as retail_value
                    FROM Products p
                    LEFT JOIN Categories c ON p.category_id = c.id
                    ORDER BY stock_status, p.name
                """)
                
                products = [dict(row) for row in cursor.fetchall()]
                
                # Get inventory status for variants
                cursor.execute("""
                    SELECT 
                        pv.id as variant_id,
                        p.id as product_id,
                        p.name as product_name,
                        pv.attribute_values,
                        pv.stock as current_stock,
                        pv.price_adjustment,
                        COALESCE(p.purchase_price, 0) as base_cost,
                        COALESCE(p.unit_price, 0) as base_price,
                        COALESCE(p.unit_price, 0) + COALESCE(pv.price_adjustment, 0) as variant_price,
                        CASE 
                            WHEN pv.stock <= 0 THEN 'low'
                            WHEN pv.stock <= 5 THEN 'warning'
                            ELSE 'ok'
                        END as stock_status
                    FROM ProductVariants pv
                    JOIN Products p ON pv.product_id = p.id
                    WHERE p.has_variants = 1
                    ORDER BY p.name, pv.id
                """)
                
                variants_rows = cursor.fetchall()
                variants = []
                
                for row in variants_rows:
                    variant_data = dict(row)
                    
                    # Parse attribute_values
                    try:
                        if variant_data.get('attribute_values'):
                            if isinstance(variant_data['attribute_values'], str):
                                variant_data['attributes'] = json.loads(variant_data['attribute_values'])
                            else:
                                variant_data['attributes'] = variant_data['attribute_values']
                                
                            # Create a display name for the variant
                            if isinstance(variant_data['attributes'], dict):
                                variant_data['variant_name'] = " / ".join(str(v) for v in variant_data['attributes'].values() if v)
                            else:
                                variant_data['variant_name'] = f"Variant #{variant_data.get('variant_id', '')}"
                    except:
                        variant_data['attributes'] = {}
                        variant_data['variant_name'] = f"Variant #{variant_data.get('variant_id', '')}"
                        
                    # Calculate stock value
                    variant_price = variant_data.get('variant_price', 0)
                    variant_data['stock_value'] = variant_price * variant_data.get('current_stock', 0)
                        
                    variants.append(variant_data)
                
                # Calculate summary statistics
                total_products = len(products)
                low_stock_products = sum(1 for p in products if p.get('stock_status') == 'low')
                warning_stock_products = sum(1 for p in products if p.get('stock_status') == 'warning')
                total_stock_value = sum(p.get('stock_value', 0) or 0 for p in products)
                total_retail_value = sum(p.get('retail_value', 0) or 0 for p in products)
                
                # Add variant stock value to total
                total_stock_value += sum(v.get('stock_value', 0) or 0 for v in variants)
                
                summary = {
                    'total_products': total_products,
                    'low_stock_products': low_stock_products,
                    'warning_stock_products': warning_stock_products,
                    'total_stock_value': total_stock_value,
                    'total_retail_value': total_retail_value,
                    'potential_profit': total_retail_value - total_stock_value
                }
                
                return {
                    'summary': summary,
                    'products': products,
                    'variants': variants
                }
            except Exception as e:
                print(f"Error getting inventory report: {e}")
                return None
            finally:
                conn.close()
        return None

    @staticmethod
    def get_profit_margin_report(start_date=None, end_date=None):
        """Get profit margin report for all products sold in a period"""
        conn = get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                
                # Format date strings if provided
                params = []
                date_filter = ""
                if start_date:
                    start_date_str = f"{start_date} 00:00:00"
                    params.append(start_date_str)
                    date_filter += " AND s.created_at >= ?"
                    
                if end_date:
                    end_date_str = f"{end_date} 23:59:59"
                    params.append(end_date_str)
                    date_filter += " AND s.created_at <= ?"
                
                # Overall profit summary
                cursor.execute(f"""
                    SELECT 
                        SUM(si.subtotal) as total_revenue,
                        SUM(si.quantity * si.unit_cost) as total_cost,
                        SUM(si.subtotal - (si.quantity * si.unit_cost)) as total_profit,
                        (SUM(si.subtotal - (si.quantity * si.unit_cost)) / SUM(si.subtotal)) * 100 as margin_percentage
                    FROM SaleItems si
                    JOIN Sales s ON si.sale_id = s.id
                    WHERE 1=1 {date_filter}
                """, params)
                
                overall_summary = dict(cursor.fetchone() or {})
                
                # Product-level profit margin
                cursor.execute(f"""
                    SELECT 
                        p.id as product_id,
                        p.name as product_name,
                        COALESCE(c.name, 'Non catégorisé') as category_name,
                        SUM(si.quantity) as quantity_sold,
                        SUM(si.subtotal) as revenue,
                        SUM(si.quantity * si.unit_cost) as cost,
                        SUM(si.subtotal - (si.quantity * si.unit_cost)) as profit,
                        (SUM(si.subtotal - (si.quantity * si.unit_cost)) / SUM(si.subtotal)) * 100 as margin_percentage
                    FROM SaleItems si
                    JOIN Sales s ON si.sale_id = s.id
                    JOIN Products p ON si.product_id = p.id
                    LEFT JOIN Categories c ON p.category_id = c.id
                    WHERE si.unit_cost > 0 {date_filter}
                    GROUP BY p.id
                    ORDER BY margin_percentage DESC
                """, params)
                
                products = [dict(row) for row in cursor.fetchall()]
                
                # Category-level profit margin
                cursor.execute(f"""
                    SELECT 
                        COALESCE(c.name, 'Non catégorisé') as category_name,
                        COUNT(DISTINCT p.id) as product_count,
                        SUM(si.quantity) as quantity_sold,
                        SUM(si.subtotal) as revenue,
                        SUM(si.quantity * si.unit_cost) as cost,
                        SUM(si.subtotal - (si.quantity * si.unit_cost)) as profit,
                        (SUM(si.subtotal - (si.quantity * si.unit_cost)) / SUM(si.subtotal)) * 100 as margin_percentage
                    FROM SaleItems si
                    JOIN Sales s ON si.sale_id = s.id
                    JOIN Products p ON si.product_id = p.id
                    LEFT JOIN Categories c ON p.category_id = c.id
                    WHERE si.unit_cost > 0 {date_filter}
                    GROUP BY COALESCE(c.name, 'Non catégorisé')
                    ORDER BY profit DESC
                """, params)
                
                categories = [dict(row) for row in cursor.fetchall()]
                
                # Monthly profit trend
                cursor.execute(f"""
                    SELECT 
                        strftime('%Y-%m', s.created_at) as month,
                        SUM(si.subtotal) as revenue,
                        SUM(si.quantity * si.unit_cost) as cost,
                        SUM(si.subtotal - (si.quantity * si.unit_cost)) as profit,
                        (SUM(si.subtotal - (si.quantity * si.unit_cost)) / SUM(si.subtotal)) * 100 as margin_percentage
                    FROM SaleItems si
                    JOIN Sales s ON si.sale_id = s.id
                    WHERE si.unit_cost > 0 {date_filter}
                    GROUP BY month
                    ORDER BY month
                """, params)
                
                monthly_trend = [dict(row) for row in cursor.fetchall()]
                
                return {
                    'start_date': start_date,
                    'end_date': end_date,
                    'summary': overall_summary,
                    'products': products,
                    'categories': categories,
                    'monthly_trend': monthly_trend
                }
            except Exception as e:
                print(f"Error getting profit margin report: {e}")
                return None
            finally:
                conn.close()
        return None

    @staticmethod
    def get_stock_movement_report(start_date=None, end_date=None, product_id=None):
        """Get stock movement report for products"""
        conn = get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                
                # Build query parameters
                params = []
                where_conditions = []
                
                if product_id:
                    where_conditions.append("sm.product_id = ?")
                    params.append(product_id)
                    
                if start_date:
                    where_conditions.append("sm.created_at >= ?")
                    params.append(f"{start_date} 00:00:00")
                    
                if end_date:
                    where_conditions.append("sm.created_at <= ?")
                    params.append(f"{end_date} 23:59:59")
                
                where_clause = ""
                if where_conditions:
                    where_clause = "WHERE " + " AND ".join(where_conditions)
                
                # Get movement summary by type
                cursor.execute(f"""
                    SELECT 
                        sm.movement_type,
                        COUNT(*) as movement_count,
                        SUM(sm.quantity) as total_quantity,
                        SUM(sm.quantity * sm.unit_price) as total_value
                    FROM StockMovements sm
                    {where_clause}
                    GROUP BY sm.movement_type
                    ORDER BY total_quantity DESC
                """, params)
                
                movement_summary = [dict(row) for row in cursor.fetchall()]
                
                # Get detailed movements
                cursor.execute(f"""
                    SELECT 
                        sm.id as movement_id,
                        sm.product_id,
                        p.name as product_name,
                        sm.variant_id,
                        sm.movement_type,
                        sm.quantity,
                        sm.unit_price,
                        sm.reference,
                        sm.notes,
                        u.username as user_name,
                        sm.created_at
                    FROM StockMovements sm
                    JOIN Products p ON sm.product_id = p.id
                    LEFT JOIN Users u ON sm.user_id = u.id
                    {where_clause}
                    ORDER BY sm.created_at DESC
                    LIMIT 1000
                """, params)
                
                movements = [dict(row) for row in cursor.fetchall()]
                
                # Get variant information for movements with variants
                variant_movements = [m for m in movements if m.get('variant_id')]
                
                if variant_movements:
                    variant_ids = [m['variant_id'] for m in variant_movements]
                    placeholders = ','.join(['?'] * len(variant_ids))
                    
                    cursor.execute(f"""
                        SELECT 
                            pv.id as variant_id,
                            pv.attribute_values
                        FROM ProductVariants pv
                        WHERE pv.id IN ({placeholders})
                    """, variant_ids)
                    
                    variant_data = {row['variant_id']: row for row in cursor.fetchall()}
                    
                    # Enhance movement data with variant names
                    for movement in variant_movements:
                        variant_id = movement['variant_id']
                        if variant_id in variant_data:
                            variant = variant_data[variant_id]
                            # Parse attribute values
                            try:
                                attr_values = variant.get('attribute_values', '{}')
                                if isinstance(attr_values, str):
                                    attributes = json.loads(attr_values)
                                else:
                                    attributes = attr_values
                                
                                if isinstance(attributes, dict):
                                    variant_name = " / ".join(str(v) for v in attributes.values() if v)
                                    movement['variant_name'] = variant_name
                            except:
                                movement['variant_name'] = f"Variant #{variant_id}"
                
                # Calculate summary statistics
                total_in = sum(m.get('total_quantity', 0) or 0 for m in movement_summary 
                              if m.get('movement_type') in ['purchase', 'adjustment_in', 'return'])
                
                total_out = sum(m.get('total_quantity', 0) or 0 for m in movement_summary 
                               if m.get('movement_type') in ['sale', 'adjustment_out', 'damage', 'loss'])
                
                summary = {
                    'start_date': start_date,
                    'end_date': end_date,
                    'total_movements': len(movements),
                    'total_in': total_in,
                    'total_out': total_out,
                    'net_change': total_in - total_out
                }
                
                return {
                    'summary': summary,
                    'movement_types': movement_summary,
                    'movements': movements
                }
            except Exception as e:
                print(f"Error getting stock movement report: {e}")
                return None
            finally:
                conn.close()
        return None

    @staticmethod
    def get_customer_sales_report(start_date=None, end_date=None, customer_id=None):
        """Get sales report by customer"""
        conn = get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                
                # Build query parameters
                params = []
                where_conditions = ["s.customer_id IS NOT NULL"]
                
                if customer_id:
                    where_conditions.append("s.customer_id = ?")
                    params.append(customer_id)
                    
                if start_date:
                    where_conditions.append("s.created_at >= ?")
                    params.append(f"{start_date} 00:00:00")
                    
                if end_date:
                    where_conditions.append("s.created_at <= ?")
                    params.append(f"{end_date} 23:59:59")
                
                where_clause = "WHERE " + " AND ".join(where_conditions)
                
                # Get customer sales summary
                cursor.execute(f"""
                    SELECT 
                        c.id as customer_id,
                        c.name as customer_name,
                        c.email as customer_email,
                        c.phone as customer_phone,
                        COUNT(s.id) as sale_count,
                        SUM(s.final_total) as total_spent,
                        AVG(s.final_total) as average_sale,
                        MIN(s.created_at) as first_purchase,
                        MAX(s.created_at) as last_purchase
                    FROM Sales s
                    JOIN Customers c ON s.customer_id = c.id
                    {where_clause}
                    GROUP BY c.id
                    ORDER BY total_spent DESC
                """, params)
                
                customers = [dict(row) for row in cursor.fetchall()]
                
                # If a specific customer is selected, get their detailed purchase history
                customer_purchases = []
                if customer_id:
                    cursor.execute(f"""
                        SELECT 
                            s.id as sale_id,
                            s.created_at,
                            s.total_amount as subtotal,
                            s.discount,
                            s.final_total,
                            s.payment_method,
                            COUNT(si.id) as item_count
                        FROM Sales s
                        LEFT JOIN SaleItems si ON s.id = si.sale_id
                        WHERE s.customer_id = ?
                        GROUP BY s.id
                        ORDER BY s.created_at DESC
                    """, [customer_id])
                    
                    customer_purchases = [dict(row) for row in cursor.fetchall()]
                    
                    # Get the customer's favorite products
                    cursor.execute(f"""
                        SELECT 
                            p.id as product_id,
                            p.name as product_name,
                            SUM(si.quantity) as quantity_purchased,
                            COUNT(DISTINCT s.id) as purchase_count,
                            SUM(si.subtotal) as total_spent
                        FROM SaleItems si
                        JOIN Sales s ON si.sale_id = s.id
                        JOIN Products p ON si.product_id = p.id
                        WHERE s.customer_id = ?
                        GROUP BY p.id
                        ORDER BY quantity_purchased DESC
                        LIMIT 10
                    """, [customer_id])
                    
                    favorite_products = [dict(row) for row in cursor.fetchall()]
                else:
                    favorite_products = []
                
                # Calculate overall statistics
                total_customers = len(customers)
                total_sales = sum(c.get('sale_count', 0) or 0 for c in customers)
                total_revenue = sum(c.get('total_spent', 0) or 0 for c in customers)
                
                summary = {
                    'start_date': start_date,
                    'end_date': end_date,
                    'total_customers': total_customers,
                    'total_sales': total_sales,
                    'total_revenue': total_revenue,
                    'average_per_customer': total_revenue / total_customers if total_customers > 0 else 0
                }
                
                return {
                    'summary': summary,
                    'customers': customers,
                    'customer_purchases': customer_purchases,
                    'favorite_products': favorite_products
                }
            except Exception as e:
                print(f"Error getting customer sales report: {e}")
                return None
            finally:
                conn.close()
        return None
