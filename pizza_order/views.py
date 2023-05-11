from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from .serializer import *
from .models import *
from .permission import IsOwner
from rest_framework.response import Response
from .tasks import mail_send
from django.shortcuts import render, redirect
from pizza.message import *
from django.conf import settings
import stripe
from .stripe_utils import stripe_session_create, stripe_customer_create
from rest_framework.serializers import ValidationError
from rest_framework.generics import RetrieveUpdateDestroyAPIView


class PizzaAdminView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = PizzaSerializerView
    queryset = Pizza.objects.all()

    def create(self, request, *args, **kwargs):
        user = request.user
        data = request.data
        id_shop = data['shop']
        if user.is_shop_owner and id_shop:

            if shop_data := Shop.objects.filter(id=id_shop).first():
                if user.id == shop_data.owner.id:
                    serializer = PizzaSerializer(data=data)
                    if serializer.is_valid(raise_exception=True):
                        serializer.save()
                        return Response({create}, status=200)
                return Response({nu}, status=203)
            return Response({nd}, status=204)
        return Response({nu}, status=400)

    def destroy(self, request, *args, **kwargs):
        data = kwargs['pk']
        if Shop.objects.prefetch_related('pizza_shop').filter(pizza_shop__id=data).exists():
            # this condition is to check that pizza id which is coming from FE is available or not in Shop
            data_pizza = Pizza.objects.get(id=data)
            pizza_data = CartPizza.objects.filter(pizza_id=data).first()
            order_pizza = OrderPizza.objects.filter(pizza_id=data).first()
            if pizza_data or order_pizza:
                """
                Here it is checking for pizza id is present or not in cart and order.
                If present then simply change it to is_deleted = true.
                If not present then delete it .
                """
                data_pizza.is_deleted = True
                data_pizza.save()
                return Response({delete}, status=200)
            # data_pizza.delete()
            return Response({"message": "Pizza Deleted"}, status=200)
        return Response({nd}, status=400)

    def partial_update(self, request, *args, **kwargs):
        super(PizzaAdminView, self).partial_update(request, *args, **kwargs)
        return Response({update})

    def retrieve(self, request, *args, **kwargs):
        try:
            shop_id = kwargs['pk']
            query = self.queryset.filter(shop=shop_id)
        except Exception as e:
            raise ValidationError(e) from e
        serializer = self.serializer_class(instance=query, many=True)
        return Response({"data": serializer.data}, status=200)


class PizzaDataForAll(viewsets.ModelViewSet):
    serializer_class = PizzaSerializerView
    queryset = Pizza.objects.all()

    def retrieve(self, request, *args, **kwargs):
        try:
            shop_id = kwargs['pk']
            query = self.queryset.filter(shop=shop_id)
        except Exception as e:
            raise ValidationError(e) from e
        serializer = self.serializer_class(instance=query, many=True)
        return Response({"data": serializer.data}, status=200)


class PizzaAllView(viewsets.ModelViewSet):
    serializer_class = PizzaSerializer
    queryset = Pizza.objects.all()


class AddressView(viewsets.ModelViewSet):
    permission_classes = [IsOwner]
    serializer_class = AddressSerializer
    lookup_field = 'pk'

    def get_queryset(self):
        user = self.request.user
        return Address.objects.filter(user=user)


class AddressWrite(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsOwner]
    serializer_class = AddressWriteSerializer
    queryset = Address.objects.all()
    lookup_field = 'pk'

    def destroy(self, request, *args, **kwargs):
        super(AddressWrite, self).destroy(request, *args, **kwargs)
        return Response({delete})

    def partial_update(self, request, *args, **kwargs):
        super(AddressWrite, self).partial_update(request, *args, **kwargs)
        return Response({update})


class AddressCreate(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, ]
    serializer_class = AddressWriteSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({'data': serializer.data})
        return Response({'error': serializer.errors})


class CartView(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsOwner]
    queryset = CartPizza.objects.all()
    # queryset =
    lookup_field = 'pk'

    def create(self, request, *args, **kwargs):
        user = self.request.user
        data = request.data
        cart, _ = Cart.objects.get_or_create(user=user)
        pizza_id_data = data.get('pizza')
        pizza_data = Pizza.objects.filter(id=pizza_id_data, is_deleted=False).first()
        try:
            cartpizza_data = CartPizza.objects.filter(cart__user=request.user).first()
        except CartPizza.DoesNotExist:
            cartpizza_data = None
        if cartpizza_data:
            if pizza_data.shop.id == cartpizza_data.shop.id:
                if item_data := CartPizza.objects.filter(pizza=pizza_id_data, cart__user=request.user).all().first():
                    item_data.quantity += 1
                    item_data.total_amount += item_data.pizza.price * int(data.get('quantity'))
                    item_data.save()
                    cart = Cart.objects.get(user=user)
                    cart.total_amount += item_data.pizza.price
                    cart.save()
                else:
                    CartPizza.objects.create(pizza_id=data.get('pizza'), cart=cart, quantity=data.get('quantity'),
                                             shop_id=pizza_data.shop.id)
                return Response({create}, status=status.HTTP_201_CREATED)
            return Response({nd}, status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            CartPizza.objects.create(pizza_id=data.get('pizza'), cart=cart, quantity=data.get('quantity'),
                                     shop_id=pizza_data.shop.id)
            return Response({create}, status=status.HTTP_201_CREATED)


class CartPizzaView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    # serializer_class = CartPizzaSerializer
    serializer_class = CartGetSerializer
    queryset = Cart.objects.all()
    lookup_field = 'pk'

    def destroy(self, request, *args, **kwargs):
        super(CartPizzaView, self).destroy(self, request, *args, **kwargs)
        return Response({delete})

    def retrieve(self, request, *args, **kwargs):
        query = self.queryset.filter(user=request.user).all()
        serializer = self.get_serializer(instance=query, many=True)
        return Response(serializer.data)


class OrderCreate(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsOwner]
    serializer_class = OrderSerializer

    def create(self, request, *args, **kwargs):
        user = request.user
        data = request.data.copy()
        print(data)
        address = Address.objects.filter(id=data.get('address'), user=user).first()
        if address:
            cart = Cart.objects.filter(user=user).first()
            print(cart.total_amount)
            shop_data = cart.cartpizza_set.all().filter(cart=cart).first()
            if cart.total_amount > 0:
                self.check_object_permissions(request, cart)
                data['total_amount'] = cart.total_amount
                serializer = OrderSerializer(data={**data, "shop": shop_data.shop.id}, context={"request": request})
                if serializer.is_valid(raise_exception=True):
                    order = serializer.save()
                    mail_send.delay("Order done", order.user.email, "Order of Pizza")
                    log = {
                        "order": order.id,
                        "status": order.status.id
                    }
                    status_log = StatusSerializerSignal(data=log)
                    if status_log.is_valid(raise_exception=True):
                        status_log.save()
                    for pizza_data in CartPizza.objects.filter(cart=cart):
                        OrderPizza.objects.create(order_id=order.id, pizza=pizza_data.pizza,
                                                  price=pizza_data.pizza.price,
                                                  quantity=pizza_data.quantity,
                                                  total_amount=pizza_data.total_amount)
                    metadata = {
                        'id': serializer.data.get('id'),
                        'user': serializer.data.get('user')

                    }
                    pay_data = {
                        "price_data": {
                            "currency": "inr",
                            "unit_amount": int(cart.total_amount) * 100,
                            "product_data": {
                                "name": cart,
                                "metadata": metadata,
                            },
                        },
                        "quantity": 1
                    }
                    session = stripe_session_create(pay_data)
                    stripe_customer_create(user, cart)
                    cart.pizza.clear()  # this is used clear all data from its associate table
                    cart.total_amount = 0
                    cart.save()
                    # invoice_sender(items, cart, user)
                    return Response({session.url})
                return Response({no_order})
            return Response({no_items})
        return Response({no_address})


def login_request(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(email=email, password=password)
        if user:
            login(request, user)
            if user.is_delivery_boy:
                return redirect('order_delivered')
            elif user.is_shop_owner:
                return redirect('shop_owner')
            else:
                return redirect('home')
        else:
            return redirect('/')
    else:
        messages.error(request, 'invalid form data')
    return render(request, 'login.html')


def order_status(request, order_idd):
    order = Order.objects.get(user=request.user, order_idd=order_idd)
    if order:
        context = {'order': order}
    else:
        context = {'order': "1"}
    return render(request, 'order.html', context)


def home(request):
    order = Order.objects.filter(user=request.user)
    if order:
        context = {'order': order}
    else:
        context = {'order': "1"}
    return render(request, 'home.html', context)


def success_payment(request):
    return render(request, 'success.html')


def cancel_payment(request):
    return render(request, 'cancel.html')


@csrf_exempt
def stripe_webhook(request):
    print("hello")
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        payment_intent = stripe.checkout.Session.list(
            payment_intent=session["payment_intent"],
            expand=['data.line_items']
        )
        product_id = payment_intent['data'][0]['line_items']['data'][0]['price']['product']
        product = stripe.Product.retrieve(product_id)
        order_id = product['metadata']['id']
        order_obj = Order.objects.filter(id=order_id).first()
        if session.payment_status == "paid":
            order_obj.is_payed = True
            order_obj.save()
    return HttpResponse(status=200)


def order_delivered(request):
    return render(request, 'order_delivered.html')


def order_delivered_url(request, id, data):
    order_data = Order.objects.filter(id=id).first()
    delivery_boy = DeliveryBoy.objects.filter(order_id=id).first()
    if not delivery_boy:
        serializer = DeliveryBoySerializer(data={
            'order_id': id
        }, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            order_data.is_delivered = True
            order_data.save()
            return HttpResponse(f"Order Accepted of {request.user}")
    return HttpResponse("Order already accepted")


class ShopCreate(viewsets.ModelViewSet):
    permission_classes = [IsOwner]
    serializer_class = ShopSerializer
    queryset = Shop.objects.all()
    lookup_field = 'pk'

    def create(self, request, *args, **kwargs):
        data = request.data
        user = request.user
        if type(user) == AnonymousUser:
            return Response({"message": "No user found"}, status=status.HTTP_401_UNAUTHORIZED)
        if user.is_shop_owner:
            shop_data = ShopSerializer(data=data, context={
                'request': request
            })
            if shop_data.is_valid(raise_exception=True):
                shop_data.save()
                return Response({create})
        return Response({nu})

    def retrieve(self, request, *args, **kwargs):
        user_id = kwargs["pk"]
        query = self.queryset.filter(owner_id=user_id)
        serialize_data = self.serializer_class(instance=query, many=True)
        return Response({"message": serialize_data.data}, status=200)

    def partial_update(self, request, *args, **kwargs):
        data_id = kwargs['pk']
        shop_user = Shop.objects.filter(id=data_id).first()
        self.check_object_permissions(request, shop_user)
        super(ShopCreate, self).partial_update(self, request, *args, **kwargs)
        return Response({update})

    def destroy(self, request, *args, **kwargs):

        data_id = kwargs['pk']
        shop_user = Shop.objects.filter(id=data_id).first()
        self.check_object_permissions(request, shop_user)
        super(ShopCreate, self).destroy(self, request, *args, **kwargs)
        return Response({delete})


@login_required
def shop_owner(request):
    return render(request, 's_owner.html')


class CartItemView(RetrieveUpdateDestroyAPIView):
    queryset = CartPizza.objects.all().prefetch_related('cart', 'pizza')
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        user = request.user
        data = request.data
        cart, _ = Cart.objects.get_or_create(user=user)
        pizza_id = data.get('pizza')
        cart = Cart.objects.get(user=user)
        if item_data := CartPizza.objects.filter(pizza=pizza_id, cart__user=request.user).all().first():
            if data.get('quantity') == -1:
                if item_data.quantity == 1:
                    item_data.delete()
                    return Response({"message": "No Pizza Left in Cart"})
                item_data.quantity -= 1
                item_data.total_amount -= item_data.pizza.price
                item_data.save()
                cart.total_amount -= item_data.pizza.price
                cart.save()
            else:
                item_data.quantity += 1
                item_data.total_amount += item_data.pizza.price
                item_data.save()
                cart.total_amount += item_data.pizza.price
                cart.save()
        return Response({"message": "No any Pizza"})
