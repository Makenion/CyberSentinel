def parse_vector(vector_string):
    traducciones = {
        "AV:N": "🌐 Acceso Remoto (Red)",
        "AV:A": "📶 Red Adyacente",
        "AV:L": "💻 Acceso Local",
        "AV:P": "🔌 Acceso Físico Requerido",
        "AC:L": "✅ Complejidad Baja",
        "AC:H": "⚠️ Complejidad Alta",
    }
    desc = [traducciones.get(part, part) for part in vector_string.split('/') if part in traducciones]
    return " | ".join(desc)