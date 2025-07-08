#!/usr/bin/env python3
"""
Servidor simple para diagnóstico de QR WhatsApp Web
"""

from flask import Flask, send_file
import os

app = Flask(__name__)

@app.route('/diagnostico-qr')
def diagnostico_qr():
    """Servir página de diagnóstico"""
    return send_file('/mnt/c/Users/PC/PYTHON/Auraai2/diagnostico_qr_simple.html')

@app.route('/test-qr')
def test_qr():
    """Endpoint de prueba para QR"""
    return {
        'success': True,
        'qr_data': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAeoAAAHqAQAAAADjFjCXAAAECElEQVR4nO2dTY6jSBCFXwxIXmKpD1BHSW426iPNDeAoPkBLsCwJ680iIzIB78Att9svFlZB8YlCeop/XEacsPGfMzQgXLhw4cKFCxcu/Lm4ubUAcDezKwDMZtbXQ9zN+jku7Z93d+EfiieS5ARYP7cAZjOM14Yc5gs54G5mdiGAhiTJLX7y7sI/FJ/dffHnF8mhI4FugfW4G9IEIHEBBwDhE594d+Gfhbe7Y0N3b5Fu7WLp1i4cv5YWmH8QowEPbZa3fnbhr8L3quPYtyDwbRyvDcyvuBsT762l/596d+GfiYfqOgKYAUvTFZYGwND9MqCbAHRLi7FvaMDW4b31swt/MT6alVK1ITBfiHS7EOnWwvr5Qvt3ApArXDN76t2FfxiefV11XwS+Dei+Lf80fi0Aunpum9q99bMLfxWOVR8kTQDQLf6Rpobk1BBpAjh0JIduQf4gSQ5v/ezCX4WHfHIfzgVHZsHB+yVuiyOJi3f4pDrhZ/Du2zBaC6Rb64c5w0ND62fLh+QE8Oe1IYdn3l34Z+ErXxduDjm4eoTNvs4dXnZzOf7K1wk/bK6mCeu8zgdkrkS3PK9gdnPK64SfsKo6DivB1QuaSOsmYKVE+Trhx81r2JUPW7A6HNB45coIuBF6pTrhR23l67KQupLDTVE0pChpazUr1Qk/YVzZFH5t2MTVfN3Q7donUp3wo7aqTVPUq1E5RPsuC24qTEdKdcJPWOR1kbkNkdLl5C7PJko2N8APFWGFn8V9jbhbkNeIs6+bLeawc4uoXBdgvDbaJRZ+xlY1rMfQMn0lo30M/4UHXEB5nfAztsvrImkrU4raV4kgrDms8CfWsAOiQffg9TYVhvp1wp+Cj+aZm/VA/sjVbM7rqhLnC+t1f8gfL/zd8FWE9dlEbdp13irO15VzMaWQrxN+1GozeNUHTrHLGdP/stoJLzOU1wk/YZsRRPTr6ri1NIjDJ/risXyd8BPm8ulcfajLm7uWSmkV+zmpTvhhcx9W1zhLq66MKoBo2nG93ynVCT9q4eE8r9s7N9Q3c2ItAHXnTqoTfsjC1wG1XnVfV4vbUtLWhWKpTvhxqxE27xIX5xYTsRJXyyWa/gs/hz++N5EtUrpyLjK8+K1UJ/y4cWsRUsv0i8um4CA1hxV+Fs/fOBFfW9IsABqan2mI0RoC8xUcrzBg/rFgvP6KL55462cX/ip8ncMx9jZXq52lm7JfQVGEFX7cHmvYzZdNlArDy9diirDCn4enybeKOcz+TWLIxcXcbpT4W+4u/CPwR19XgiuAVV27elundPPk64Qfs11et94lZgzDyhpn5HXq1wk/ZSEuAEB5WyISOVcigP3r2VKd8MNm+u91woULFy5cuHDhfwX+Pw9RpP+hI5qqAAAAAElFTkSuQmCC',
        'message': 'QR de prueba generado exitosamente'
    }

if __name__ == '__main__':
    print("🔍 Servidor de diagnóstico WhatsApp QR")
    print("📡 Accede a: http://localhost:5001/diagnostico-qr")
    app.run(host='0.0.0.0', port=5001, debug=True)
