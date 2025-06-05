import os
import django
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_medico.settings')
django.setup()

def test_smtp_connection():
    try:
        # Crear mensaje
        msg = MIMEMultipart()
        msg['From'] = 'greenia.sistema@gmail.com'
        msg['To'] = 'nicolas.velasquez16@inacapmail.cl'
        msg['Subject'] = 'Prueba de conexión SMTP'
        
        body = 'Este es un correo de prueba para verificar la conexión SMTP.'
        msg.attach(MIMEText(body, 'plain'))
        
        # Intentar conexión SMTP
        print("Intentando conectar al servidor SMTP...")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        
        print("Intentando autenticación...")
        server.login('greenia.sistema@gmail.com', 'ratk bcvy kdqu nihy')
        
        print("Enviando correo...")
        text = msg.as_string()
        server.sendmail('greenia.sistema@gmail.com', 'nicolas.velasquez16@inacapmail.cl', text)
        
        print("Correo enviado exitosamente!")
        server.quit()
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == '__main__':
    test_smtp_connection() 