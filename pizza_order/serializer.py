from rest_framework import serializers
from .models import *


class PizzaSerializer(serializers.ModelSerializer):
    # shop = serializers.CharField()
    # pizza_img = serializers.SerializerMethodField("get_pizza_img")
    # pizza_data = serializers.SerializerMethodField()

    class Meta:
        model = Pizza
        fields = '__all__'
    # def get_pizza_img(self,obj):
    #     # return obj.pizza.image.url
    #     request = self.context.get("request")
    #     return request.build_absolute_uri(obj.image.url)

    # def get_pizza_data(self, obj):
    #     print(obj.cartpizza_set.all(),"dkf")
    #     return obj.cartpizza_set.filter


class PizzaSerializerView(serializers.ModelSerializer):
    class Meta:
        model = Pizza
        fields = "__all__"


class AddressSerializer(serializers.ModelSerializer):
    user = serializers.CharField()

    class Meta:
        model = Address
        fields = '__all__'


class AddressWriteSerializer(serializers.ModelSerializer):
    user = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Address
        fields = '__all__'


class CartSerializer(serializers.ModelSerializer):
    pizza = serializers.SlugRelatedField(many=True, read_only=True, slug_field="name")
    user = serializers.CharField(default=serializers.CurrentUserDefault())

    # shop = serializers.CharField()

    class Meta:
        model = Cart
        fields = '__all__'





class CartPizzaSerializer(serializers.ModelSerializer):
    pizza = serializers.CharField()
    # shop = serializers.CharField()
    # cart = serializers.CharField()
    pizza_img = serializers.SerializerMethodField("get_pizza_img")
    pizza_data = serializers.SerializerMethodField()

    class Meta:
        model = CartPizza
        fields = "__all__"

    def get_pizza_img(self, obj):
        request = self.context.get("request")
        return request.build_absolute_uri(obj.pizza.image.url)

    def get_pizza_data(self, obj):
        return {"price": obj.pizza.price, "size": obj.pizza.size, "id": obj.pizza.id}


class CartGetSerializer(serializers.ModelSerializer):
    user = serializers.CharField(default=serializers.CurrentUserDefault())
    data_pizza = CartPizzaSerializer(source="cartpizza_set", read_only=True, many=True)

    class Meta:
        model = Cart
        fields = ['id', 'total_amount', 'user', 'data_pizza']


class OrderSerializer(serializers.ModelSerializer):
    pizza = PizzaSerializer(many=True, read_only=True)
    user = serializers.CharField(default=serializers.CurrentUserDefault())
    total_amount = serializers.IntegerField()

    class Meta:
        model = Order
        fields = '__all__'


class OrderSerializerSignal(serializers.ModelSerializer):
    pizza = PizzaSerializer(many=True, read_only=True)
    # pizza = serializers.CharField()
    user = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Order
        fields = "__all__"


class DeliveryBoySerializer(serializers.ModelSerializer):
    delivery_boy = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = DeliveryBoy
        fields = "__all__"


class ShopSerializer(serializers.ModelSerializer):
    owner = serializers.CharField(default=serializers.CurrentUserDefault())
    # owner = serializers.CharField()

    class Meta:
        model = Shop
        fields = '__all__'



class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = "__all__"


class StatusLogSerializer(serializers.ModelSerializer):
    # order = serializers.CharField(read_only=True)
    status = StatusSerializer()
    class Meta:
        model = StatusLog
        fields = "__all__"

class StatusSerializerSignal(serializers.ModelSerializer):
    class Meta:
        model = StatusLog
        fields = "__all__"


class CartUserDetailsSerializer(serializers.ModelSerializer):
    pizza = serializers.CharField()
    # pizza_data = PizzaSerializer()

    class Meta:
        model=CartPizza
        fields = "__all__"

    # def to_representation(self, instance):
    #     representation = super().to_representation(instance)
    #     print(instance.quantity,"ins")
    #     # representation['total_quantity']=0
    #     representation['total_quantity'] += instance.quantity
    #     return representation


class CartItemPizzaSerializer(serializers.ModelSerializer):
    # data = CartUserDetailsSerializer(source="cartpizza_set",many=True)
    # user = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Cart
        fields = "__all__"


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartPizza
        fields = "__all__"
