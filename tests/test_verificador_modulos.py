import unittest
import sys
import os
from unittest.mock import patch, MagicMock
from pathlib import Path

# Asegurar que podemos importar desde el directorio raíz
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from clientes.aura.routes.admin_modulos.verificador.registro import modulo_parece_registrado
from clientes.aura.routes.admin_modulos.verificador.file_utils import buscar_en_init, contiene_blueprint
from clientes.aura.routes.admin_modulos.verificador.http_checker import verificar_respuesta_http

class TestVerificadorModulos(unittest.TestCase):
    """Pruebas unitarias para el verificador de módulos."""
    
    def test_modulo_parece_registrado(self):
        """Prueba la detección heurística de registro."""
        contenido_valido = """
        from clientes.aura.routes.panel_cliente_test import panel_cliente_test_bp
        if "test" in modulos:
            safe_register_blueprint(app, panel_cliente_test_bp, 
                url_prefix=f"/panel_cliente/{nombre_nora}/test")
        """
        
        resultado = modulo_parece_registrado("test", contenido_valido)
        self.assertTrue(resultado["parece_registrado"])
        self.assertEqual(resultado["nivel_confianza"], "alto")
        
        contenido_invalido = """
        # Este módulo no está registrado
        pass  # test desactivado
        """
        
        resultado = modulo_parece_registrado("test", contenido_invalido)
        self.assertFalse(resultado["parece_registrado"])
    
    def test_buscar_en_init(self):
        """Prueba la búsqueda en __init__.py"""
        contenido = """
        from clientes.aura.routes.panel_cliente_test import panel_cliente_test_bp
        from .panel_cliente_otro import panel_cliente_otro_bp
        """
        
        resultados = buscar_en_init("test", contenido)
        self.assertTrue(len(resultados) > 0)
        
        resultados = buscar_en_init("inexistente", contenido)
        self.assertEqual(len(resultados), 0)
    
    @patch('requests.get')
    def test_verificar_respuesta_http(self, mock_get):
        """Prueba la verificación HTTP."""
        # Configurar el mock para simular respuesta 200
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_get.return_value = mock_response
        
        resultado = verificar_respuesta_http("/ruta/test")
        self.assertTrue(resultado["existe"])
        self.assertEqual(resultado["status"], 200)
        
        # Configurar el mock para simular respuesta 404
        mock_response.status_code = 404
        resultado = verificar_respuesta_http("/ruta/inexistente")
        self.assertFalse(resultado["existe"])
        self.assertEqual(resultado["status"], 404)

if __name__ == '__main__':
    unittest.main()