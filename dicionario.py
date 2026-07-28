import sqlite3
import streamlit as st

# Configuração da página do navegador
st.set_page_config(page_title="Dicionário Conlang", page_icon="📚", layout="centered")

# Conexão com o banco de dados
def get_connection():
    # check_same_thread=False é necessário para o SQLite funcionar bem com o Streamlit
    conn = sqlite3.connect('meu_dicionario.db', check_same_thread=False)
    return conn

conn = get_connection()
cursor = conn.cursor()

# Criação da tabela
cursor.execute('''
CREATE TABLE IF NOT EXISTS palavras (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pt TEXT UNIQUE,
    conlang TEXT UNIQUE
)
''')
conn.commit()

# Título Principal
st.title("📚 Dicionário da Nova Língua")
st.caption("Acesse, adicione e gerencie as palavras do seu idioma de qualquer lugar.")

# Criando as abas de navegação visual
tab_traduzir, tab_adicionar, tab_alterar, tab_deletar, tab_listar = st.tabs([
    "🔍 Traduzir", 
    "➕ Ensinar Palavra", 
    "✏️ Alterar", 
    "🗑️ Apagar", 
    "📖 Lista Completa"
])

# ------------------ ABA 1: TRADUZIR ------------------
with tab_traduzir:
    st.header("Traduzir Termos")
    
    opcao_traducao = st.radio("Direção da tradução:", ["Português ➡️ Nova Língua", "Nova Língua ➡️ Português"])
    termo = st.text_input("Digite a palavra para pesquisar:")
    
    if st.button("Buscar Tradução"):
        if termo.strip():
            termo_limpo = termo.strip().lower()
            if opcao_traducao == "Português ➡️ Nova Língua":
                cursor.execute("SELECT conlang FROM palavras WHERE pt = ?", (termo_limpo,))
                res = cursor.fetchone()
                if res:
                    st.success(f"**{termo.capitalize()}** em sua língua é: **{res[0].capitalize()}**")
                else:
                    st.warning(f"A palavra '{termo}' não foi encontrada no dicionário.")
            else:
                cursor.execute("SELECT pt FROM palavras WHERE conlang = ?", (termo_limpo,))
                res = cursor.fetchone()
                if res:
                    st.success(f"**{termo.capitalize()}** em Português é: **{res[0].capitalize()}**")
                else:
                    st.warning(f"A palavra '{termo}' não foi encontrada no dicionário.")
        else:
            st.info("Digite um termo para realizar a busca.")

# ------------------ ABA 2: ENSINAR ------------------
with tab_adicionar:
    st.header("Cadastrar Nova Palavra")
    
    col1, col2 = st.columns(2)
    with col1:
        pt_input = st.text_input("Palavra em Português:")
    with col2:
        cl_input = st.text_input("Palavra na Nova Língua:")
        
    if st.button("Salvar Palavra"):
        if pt_input.strip() and cl_input.strip():
            try:
                cursor.execute("INSERT INTO palavras (pt, conlang) VALUES (?, ?)", 
                               (pt_input.strip().lower(), cl_input.strip().lower()))
                conn.commit()
                st.success(f"✅ Nova palavra salva: **{pt_input}** = **{cl_input}**")
            except sqlite3.IntegrityError:
                st.error("⚠️ Esta palavra (em Português ou na Nova Língua) já existe no dicionário!")
        else:
            st.warning("Preencha ambos os campos antes de salvar.")

# ------------------ ABA 3: ALTERAR ------------------
with tab_alterar:
    st.header("Alterar Significados")
    
    pt_alterar = st.text_input("Palavra em Português que deseja alterar:")
    novo_cl = st.text_input("Novo significado na sua língua:")
    
    if st.button("Atualizar Significados"):
        if pt_alterar.strip() and novo_cl.strip():
            pt_limpo = pt_alterar.strip().lower()
            cursor.execute("SELECT id FROM palavras WHERE pt = ?", (pt_limpo,))
            if cursor.fetchone():
                try:
                    cursor.execute("UPDATE palavras SET conlang = ? WHERE pt = ?", 
                                   (novo_cl.strip().lower(), pt_limpo))
                    conn.commit()
                    st.success(f"✅ Atualizado! **{pt_alterar}** agora é **{novo_cl}**.")
                except sqlite3.IntegrityError:
                    st.error("⚠️ O novo termo inserido já pertence a outra palavra no banco.")
            else:
                st.error(f"A palavra '{pt_alterar}' não existe no dicionário.")
        else:
            st.warning("Preencha todos os campos.")

# ------------------ ABA 4: DELETAR ------------------
with tab_deletar:
    st.header("Remover Palavra")
    
    pt_deletar = st.text_input("Palavra em Português que deseja excluir:")
    
    if st.button("Deletar Palavra", type="primary"):
        if pt_deletar.strip():
            pt_limpo = pt_deletar.strip().lower()
            cursor.execute("SELECT id FROM palavras WHERE pt = ?", (pt_limpo,))
            if cursor.fetchone():
                cursor.execute("DELETE FROM palavras WHERE pt = ?", (pt_limpo,))
                conn.commit()
                st.success(f"🗑️ A palavra **'{pt_deletar}'** foi removida com sucesso!")
            else:
                st.error(f"A palavra '{pt_deletar}' não foi encontrada.")
        else:
            st.warning("Digite uma palavra para deletar.")

# ------------------ ABA 5: LISTAR ------------------
with tab_listar:
    st.header("Vocabulário Completo")
    
    cursor.execute("SELECT pt, conlang FROM palavras ORDER BY pt ASC")
    dados = cursor.fetchall()
    
    if dados:
        # Formata os dados para exibir em uma tabela amigável
        lista_formatada = [{"Português": item[0].capitalize(), "Nova Língua": item[1].capitalize()} for item in dados]
        st.dataframe(lista_formatada, use_container_width=True)
        st.caption(f"Total de palavras cadastradas: **{len(dados)}**")
    else:
        st.info("Nenhuma palavra cadastrada ainda.")
