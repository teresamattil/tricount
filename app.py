import streamlit as st

class Usuario:
    def __init__(self, nombre):
        self.nombre = nombre
        self.consumido = 0.0
        self.pagado = 0.0

    @property
    def saldo(self):
        return self.pagado - self.consumido

    def __str__(self):
        return f"{self.nombre}: pagado={self.pagado:.2f} €, consumido={self.consumido:.2f} €, saldo={self.saldo:.2f} €"

class Item:
    def __init__(self, nombre, precio, usuarios, participacion, pagador):
        self.nombre = nombre
        self.precio = precio
        self.usuarios = usuarios

        self.participacion = {u.nombre: 1 if u.nombre in participacion else 0 for u in usuarios}
        self.total_personas = sum(self.participacion.values())
        self.precio_por_persona = self.precio / self.total_personas if self.total_personas > 0 else 0

        self.pagado_por = {u.nombre: 1 if u.nombre == pagador else 0 for u in usuarios}

        # Actualizar saldo de cada usuario
        for usuario in usuarios:
            if self.participacion[usuario.nombre]:
                usuario.consumido += self.precio_por_persona
            if self.pagado_por[usuario.nombre]:
                usuario.pagado += self.precio

def simplificar_deudas(usuarios):
    acreedores = [(u.nombre, u.saldo) for u in usuarios if u.saldo > 0]
    deudores = [(u.nombre, -u.saldo) for u in usuarios if u.saldo < 0]
    
    acreedores.sort(key=lambda x: x[1], reverse=True)
    deudores.sort(key=lambda x: x[1], reverse=True)
    
    transacciones = []
    
    i, j = 0, 0
    while i < len(deudores) and j < len(acreedores):
        deudor_nombre, deuda = deudores[i]
        acreedor_nombre, credito = acreedores[j]
        
        pago = min(deuda, credito)
        
        transacciones.append(f"{deudor_nombre} paga {pago:.2f} € a {acreedor_nombre}")
        
        deuda -= pago
        credito -= pago
        
        if deuda == 0:
            i += 1
        else:
            deudores[i] = (deudor_nombre, deuda)
        
        if credito == 0:
            j += 1
        else:
            acreedores[j] = (acreedor_nombre, credito)
    
    return transacciones

# Configuración de página
st.set_page_config(page_title="Tricount App", layout="centered")

# Estados iniciales
if "usuarios" not in st.session_state:
    st.session_state.usuarios = []

if "gastos" not in st.session_state:
    st.session_state.gastos = []

# Navegación lateral
st.sidebar.title("Navegación")
seccion = st.sidebar.radio("Ir a:", ["Usuarios", "Gastos", "Resultados"])

st.title("Tricount App")

# === SECCIÓN 1: AÑADIR USUARIOS ===
if seccion == "Usuarios":
    st.header("Añadir miembros al grupo")
    nombre_usuario = st.text_input("Nombre del usuario")
    if st.button("➕ Añadir usuario") and nombre_usuario:
        st.session_state.usuarios.append(Usuario(nombre_usuario))
        st.success(f"Usuario '{nombre_usuario}' añadido.")

    if st.session_state.usuarios:
        st.subheader("Miembros actuales:")
        for u in st.session_state.usuarios:
            st.markdown(f"- {u.nombre}")

# === SECCIÓN 2: AÑADIR GASTOS ===
elif seccion == "Gastos":
    st.header("Gastos del grupo")
    
    if not st.session_state.usuarios:
        st.warning("Primero añade al menos un usuario.")
    else:
        # Mostrar lista de gastos existentes
        if st.session_state.gastos:
            for item in st.session_state.gastos:
                pagador = [k for k, v in item.pagado_por.items() if v][0]
                participantes = [nombre for nombre, participa in item.participacion.items() if participa]
                st.markdown(f"- **{item.nombre}**: {item.precio:.2f} € pagado por **{pagador}**, dividido entre {len(participantes)} personas: {', '.join(participantes)}")
        else:
            st.info("No hay gastos registrados aún.")

        st.divider()

        # Botón para mostrar formulario
        if "mostrar_formulario" not in st.session_state:
            st.session_state.mostrar_formulario = False

        if not st.session_state.mostrar_formulario:
            if st.button("➕ Añadir nuevo gasto"):
                st.session_state.mostrar_formulario = True
        else:
            with st.form("nuevo_item"):
                st.subheader("➕ Añadir nuevo gasto")

                nombre_item = st.text_input("Nombre del ítem")
                precio_item = st.number_input("Precio total (€)", min_value=0.0, format="%.2f")

                st.markdown("¿Quién ha participado?")
                participacion = st.multiselect("Selecciona participantes", [u.nombre for u in st.session_state.usuarios])

                st.markdown("¿Quién ha pagado?")
                pagador = st.selectbox("Selecciona pagador", [u.nombre for u in st.session_state.usuarios])

                col1, col2 = st.columns(2)
                with col1:
                    submitted = st.form_submit_button("✅ Guardar gasto")
                with col2:
                    cancelar = st.form_submit_button("❌ Cancelar")

                if submitted and nombre_item and precio_item > 0 and participacion:
                    item = Item(nombre_item, precio_item, st.session_state.usuarios, participacion, pagador)
                    st.session_state.gastos.append(item)
                    st.session_state.mostrar_formulario = False
                    st.success(f"Gasto '{nombre_item}' añadido.")

                elif cancelar:
                    st.session_state.mostrar_formulario = False


# === SECCIÓN 3: RESULTADOS ===
elif seccion == "Resultados":

    if not st.session_state.gastos:
        st.info("Aún no se han añadido gastos.")
    else:
        st.subheader("Saldo de cada usuario")
        for u in st.session_state.usuarios:
            st.text(str(u))

        st.subheader("Transacciones sugeridas")
        transacciones = simplificar_deudas(st.session_state.usuarios)
        if transacciones:
            for t in transacciones:
                st.write("• " + t)
        else:
            st.success("Todos los saldos están equilibrados 🎉")

