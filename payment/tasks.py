from io import BytesIO
from celery import task
import weasyprint
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings
from orders.models import Order



@task
def payment_completed(order_id):
    """
    Buyurtma berilganda elektron pochta xabarnomasini yuborish vazifasi
    muvaffaqiyatli yaratildi.
    """
    order = Order.objects.get(id=order_id)
    # faktura elektron pochtasini yaratish
    subject = f'My Shop - EE Invoice no. {order.id}'
    message = 'Please, find attached the invoice for your recent purchase.'
    email = EmailMessage(subject,message,'webdewoloper@gmail.com',[order.email])
    # PDF yaratish
    html = render_to_string('orders/order/pdf.html', {'order': order})
    out = BytesIO()
    stylesheets=[weasyprint.CSS(settings.STATIC_ROOT + 'css/pdf.css')]
    weasyprint.HTML(string=html).write_pdf(out,
    stylesheets=stylesheets)
    # PDF faylni biriktiring
    email.attach(f'order_{order.id}.pdf',out.getvalue(),'application/pdf')
    # e-mail yuboring
    email.send()