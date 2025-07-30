def obtener_info_modelo():
    nombre = input("Nombre del modelo de IA: ")
    costo_entrada = float(input("Costo por 1,000,000 tokens de entrada (USD): "))
    costo_salida = float(input("Costo por 1,000,000 tokens de salida (USD): "))
    tokens_entrada = int(input("Tokens de entrada estimados: "))
    tokens_salida = int(input("Tokens de salida estimados: "))

    costo_total = (tokens_entrada / 1_000_000) * costo_entrada + (tokens_salida / 1_000_000) * costo_salida

    return {
        "nombre": nombre,
        "costo_total": costo_total,
        "entrada": costo_entrada,
        "salida": costo_salida,
        "tokens_entrada": tokens_entrada,
        "tokens_salida": tokens_salida
    }

def main():
    print("💡 Comparador de modelos IA por costo (entrada + salida) [por millón de tokens]\n")

    modelos = []
    cantidad = int(input("¿Cuántos modelos quieres comparar? "))

    for i in range(cantidad):
        print(f"\n🔹 Modelo #{i+1}")
        modelo = obtener_info_modelo()
        modelos.append(modelo)

    # Ordenar por el costo total
    modelos.sort(key=lambda x: x["costo_total"])

    print("\n📊 Resultados del cálculo:")
    for m in modelos:
        print(f"➡️ {m['nombre']}: ${m['costo_total']:.4f} USD "
              f"({m['tokens_entrada']} IN / {m['tokens_salida']} OUT)")

    print(f"\n✅ Modelo más barato: **{modelos[0]['nombre']}** (${modelos[0]['costo_total']:.4f} USD)")

if __name__ == "__main__":
    main()
