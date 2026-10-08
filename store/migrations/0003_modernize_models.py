from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0002_alter_product_image"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customer",
            name="email",
            field=models.EmailField(max_length=200),
        ),
        migrations.AlterField(
            model_name="product",
            name="digital",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="orderitem",
            name="quantity",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="shippingaddress",
            name="country",
            field=models.CharField(default="India", max_length=100),
        ),
        migrations.AlterField(
            model_name="shippingaddress",
            name="zipcode",
            field=models.CharField(max_length=20),
        ),
    ]
