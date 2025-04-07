def normalizar_numero(numero: str) -> str:
    if numero is None:
        return ""
    
    numero = numero.strip().replace("whatsapp:", "").replace("+", "").replace("-", "").replace(" ", "")
    
    if not numero.startswith("521"):
        numero = "521" + numero
    
    return f"whatsapp:+{numero}"
