from django.test import TestCase
from products.models import Product
from users.models import User
from carts.models import Cart, CartProducts
from decimal import Decimal
from django.core.files.uploadedfile import SimpleUploadedFile

class CartTestCase(TestCase):
    def setUp(self):
        
        self.user = User.objects.create(username='testuser', email='test@example.com')
        image = SimpleUploadedFile(name='test_image.jpg', content=b'', content_type='image/jpeg')
        self.product1 = Product.objects.create(title="Lampara", description="Lampara de mesa", image=image, price=Decimal(10.00))
        self.product2 = Product.objects.create(title="Mesa", description="Mesa de madero", image=image, price=Decimal(15.00))
        self.product3 = Product.objects.create(title="Maletin", price=Decimal('-5.00'))
        self.cart = Cart.objects.create(user=self.user)

    # Prueba calcular subtotal con un solo producto    
    def test_update_subtotal(self):
    
        CartProducts.objects.create(cart=self.cart, product=self.product2, quantity=3)
        self.cart.update_subtotal()
        self.assertEqual(self.cart.subtotal, Decimal(45.00))

    # Prueba del calculo del subtotal cuando mas de 1 producto en el carrito (2*10 + 3*15 = 65)  
    def test_update_subtotal_product(self):
    
        CartProducts.objects.create(cart=self.cart, product=self.product1, quantity=2)
        CartProducts.objects.create(cart=self.cart, product=self.product2, quantity=3)
        self.cart.update_subtotal()
        self.assertEqual(self.cart.subtotal, Decimal(65.00))
        
    #Prueba cuando el carrito esta vacio
    def test_empty_cart_subtotal(self):
       
        self.cart.update_subtotal()
        self.assertEquals(self.cart.subtotal, 0)

     # Prueba cuando un producto tiene cantidad < 0
    def test_subtotal_negative_quantity(self):
       
        CartProducts.objects.create(cart=self.cart, product=self.product1, quantity=-3)
        self.cart.update_subtotal()
        # Espero que subtotal ≥ 0 
        self.assertGreaterEqual(self.cart.subtotal, 0 , f"Subtotal es negativo ({self.cart.subtotal}); debería ser al menos 0")

    # Prueba cuando un producto tiene precio < 0
    def test_subtotal_negative_price(self):
    
        CartProducts.objects.create(cart=self.cart, product=self.product3, quantity=2)
        self.cart.update_subtotal()
        # ¡Aquí esperamos que sea >= 0! 
        self.assertGreaterEqual(self.cart.subtotal, 0, f"Subtotal es negativo ({self.cart.subtotal}); debería ser al menos 0")


    








#     # Prueba que suma cantidades cuando el producto ya está en el carrito
#     def test_update_existing_cart_product_quantity(self):
        
#         CartProducts.objects.create(cart=self.cart, product=self.product1, quantity=1) # Agregar primero producto con cantidad 1
#         cart_product = CartProducts.objects.create_or_update_quantity(cart=self.cart, product=self.product1, quantity=3) # Luego actualizar la cantidad usando la función
#         self.assertEqual(cart_product.quantity, 4)
    
# class CartTestQuantity(TestCase):

#     def setUp(self):

#         self.user = User.objects.create(username='testuser', email='test@example.com')
#         image = SimpleUploadedFile(name='test_image.jpg', content=b'', content_type='image/jpeg')
#         self.product1 = Product.objects.create(title="Lampara", description="Lampara de mesa", image=image, price=Decimal(10.00))
    
#     # Prueba crear carrito si no existe y añadir producto con cantidad
#     def test_create_cart_and_add_product(self):

#         cart, created = Cart.objects.get_or_create(user=self.user)  # Crear carrito si no existe
#         self.assertTrue(created)  # Verificar que fue creado
#         cart_product = CartProducts.objects.create_or_update_quantity(cart=cart, product=self.product1)  # Agregar producto
#         self.assertEqual(cart_product.quantity, 1)  # Verificar cantidad
    
    







