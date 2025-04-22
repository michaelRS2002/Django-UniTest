from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from carts.models import Cart
from orders.models import Order, OrderStatus
from django.urls import reverse

User = get_user_model()

class OrderTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.cart = Cart.objects.create(user=self.user)
    # 1. Acceso a Orden  --> No pasaria si este no redirige a LOGIN 
    def test_order_view_requires_login(self):
        response = self.client.get(reverse('orders:order')) 
        self.assertRedirects(response, '/usuarios/login?next=/orden/')
    # 2.Obtener Carrito --> No pasa si no se creara la orden o no trajera bien los valores
    def test_order_created_with_uuid_and_total(self):
        order = Order.objects.create(user=self.user, cart=self.cart)
        self.assertIsNotNone(order.order_id)
        self.assertEqual(order.status.name, OrderStatus.CREATED.name)
        self.assertEqual(order.total, self.cart.total + order.shipping_total)
    #2.2 Suma de taxes --> No pasa si no se sumara bien la compra el envio y los impuestos
    def test_get_total_returns_correct_value(self):
        order = Order.objects.create(user=self.user, cart=self.cart)
        expected_total = self.cart.total + order.shipping_total
        self.assertEqual(order.get_total(), expected_total)
    #2.3 Actualizar total de la compra si se añade algo al carrito --> No pasa si no se actualiza
    def test_update_total_sets_correct_total(self):
        order = Order.objects.create(user=self.user, cart=self.cart)
        order.shipping_total = 10.00
        order.update_total()
        expected = order.cart.total + 10.00
        self.assertEqual(order.total, expected)

    
    # 3. Creacion de orden correcta --> No pasa si no esta logiado y si esta logiado pasa a crear una orden
    def test_order_view_creates_order_if_not_exists(self):
        self.client.login(username='testuser', password='testpass')
        
        # Establecer el carrito en la sesión manualmente
        session = self.client.session
        session['cart_id'] = self.cart.cart_id
        session.save()

        # Llamada a la vista
        response = self.client.get(reverse('orders:order'))  

        # Verificaciones
        self.assertEqual(response.status_code, 200)
        order = Order.objects.filter(cart=self.cart).first()
        self.assertIsNotNone(order)
        self.assertEqual(order.user, self.user)
    #3.2 Creacion de ordenes nueva y no se duplique --> no pasa si se crean 2 ordenes 
    def test_order_view_does_not_create_duplicate_order(self):
        self.client.login(username='testuser', password='testpass')
        Order.objects.create(cart=self.cart, user=self.user)
        response = self.client.get(reverse('orders:order'))  
        self.assertEqual(Order.objects.filter(cart=self.cart).count(), 1)
    # 4. Orden Valida --> No pasa si la orden no es valida    
    def test_order_view_returns_status_200(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('orders:order'))
        self.assertEqual(response.status_code,200,msg="❌ Error: La vista de orden no devolvió status 200 como se esperaba.")
    # 4.2 Orden Valida --> No pasa si permite crear ordenes sin productos
    def test_order_view_does_not_create_order_if_cart_is_empty(self):
        self.client.login(username='testuser', password='testpass')
        # Establecer el carrito en la sesión manualmente
        self.cart.products.clear()  # Deja el carrito vacío
        session = self.client.session
        session['cart_id'] = self.cart.cart_id
        session.save()
        # Llamada a la vista
        response = self.client.get(reverse('orders:order'))
        # Verificaciones
        self.assertEqual(response.status_code, 200)
        order = Order.objects.filter(cart=self.cart).first()
        self.assertIsNone(order)  # No debería haber una orden
        #self.assertIsNone(None)
