import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def enviar_correo(destinatario, asunto, cuerpo_html):
    smtp_server = "mail.soynoraai.com"
    smtp_port = 465
    smtp_user = "tareas@soynoraai.com"
    smtp_password = "1002ivimyH!"  # Reemplaza por tu contraseña real

    msg = MIMEMultipart()
    msg["From"] = smtp_user
    msg["To"] = destinatario
    msg["Subject"] = asunto
    msg["Reply-To"] = smtp_user
    # msg.add_header('Return-Path', smtp_user)  # Algunos servidores ignoran esto, pero puedes probar
    msg.attach(MIMEText(cuerpo_html, "html"))

    print("==== DEBUG EMAIL ====")
    print("From:", smtp_user)
    print("To:", destinatario)
    print("Subject:", asunto)
    print("Body:", cuerpo_html)
    print("=====================")

    try:
        print(f"Conectando al servidor SMTP {smtp_server}:{smtp_port} ...")
        with smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=15) as server:
            print("Conexión establecida, intentando login...")
            server.login(smtp_user, smtp_password)
            print(f"Enviando correo a {destinatario} ...")
            server.sendmail(smtp_user, destinatario, msg.as_string())
            print(f"✅ Correo enviado a {destinatario}")
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Error de autenticación SMTP: {e}")
    except smtplib.SMTPConnectError as e:
        print(f"❌ Error de conexión SMTP: {e}")
    except smtplib.SMTPException as e:
        print(f"❌ Error general de SMTP: {e}")
    except Exception as e:
        print(f"❌ Error inesperado enviando correo: {e}")
