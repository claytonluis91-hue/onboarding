import streamlit as st
import requests
import re
import pandas as pd
import json
import os
from database import save_client_data, load_client_data
from pdf_generator import gerar_pdf

st.set_page_config(page_title="Ficha de Novo Cliente", layout="wide")

# Inicializar estados session_state
if "form_data" not in st.session_state:
    st.session_state.form_data = {
        "cnpj": "",
        "ie": "",
        "razao_social": "",
        "nome_fantasia": "",
        "data_abertura": "",
        "cnae_principal": "",
        "endereco": "",
        "data_inicio_cliente": "",
        "regime_tributario": "Simples Nacional",
        "contatos": [],
        "resumo_cliente": "",
        "escopo_fiscal": {},
        "qtd_notas_saida": "",
        "qtd_notas_entrada": "",
        "estados_icms_st": [],
        "escopo_contabil": {},
        "escopo_dp": {},
        "escopo_regularizacao": {},
        "estados_st": []
    }

def limpar_cnpj(cnpj):
    return re.sub(r'[^0-9]', '', cnpj)

def buscar_cnpj():
    cnpj_limpo = limpar_cnpj(st.session_state.cnpj_input)
    if len(cnpj_limpo) != 14:
        st.error("CNPJ inválido. Digite 14 números.")
        return

    # Tenta carregar do banco primeiro
    dados_banco = load_client_data(cnpj_limpo)
    if dados_banco:
        # Garante as novas chaves caso seja um draft antigo
        for key in st.session_state.form_data.keys():
            if key not in dados_banco:
                dados_banco[key] = st.session_state.form_data[key]
        st.session_state.form_data = dados_banco
        st.success("Dados carregados do banco local (Rascunho anterior encontrado)!")
        return

    # Busca na API
    try:
        response = requests.get(f"https://brasilapi.com.br/api/cnpj/v1/{cnpj_limpo}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            
            endereco = f"{data.get('logradouro', '')}, {data.get('numero', '')}"
            if data.get('complemento'):
                endereco += f" - {data.get('complemento')}"
            endereco += f" - {data.get('bairro', '')}, {data.get('municipio', '')} - {data.get('uf', '')}"
            
            st.session_state.form_data.update({
                "cnpj": cnpj_limpo,
                "razao_social": data.get("razao_social", ""),
                "nome_fantasia": data.get("nome_fantasia", ""),
                "data_abertura": data.get("data_inicio_atividade", ""),
                "cnae_principal": f"{data.get('cnae_fiscal', '')} - {data.get('cnae_fiscal_descricao', '')}",
                "endereco": endereco
            })
            st.success("Dados carregados da Receita Federal (BrasilAPI)!")
        else:
            st.error("Erro ao buscar CNPJ. Verifique o número ou tente novamente mais tarde.")
    except Exception as e:
        st.error(f"Erro de conexão com a API: {e}")

# ==================== INTERFACE ====================
st.title("📄 Ficha de Novo Cliente - Nascel")

col1, col2 = st.columns([3, 1])
with col1:
    cnpj_input = st.text_input("Digite o CNPJ", key="cnpj_input")
with col2:
    st.write("")
    st.write("")
    if st.button("Buscar Dados", use_container_width=True):
        buscar_cnpj()

st.divider()

# Listas pré-definidas
REGIMES = ["MEI", "Simples Nacional", "Lucro Presumido", "Lucro Real", "Imune/Isenta"]
SETORES = ["Sócio/Diretor", "Financeiro", "Fiscal", "Contábil", "DP/RH", "Outro"]
ESTADOS = ["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"]
OPCOES_TTS = [
    "TTS/CORREDOR DE IMPORTAÇÃO",
    "TTS/CD DE INDÚSTRIA DE OUTRA UF",
    "TTS/E-COMMERCE NÃO VINCULADO",
    "TTS/E-COMMERCE VINCULADO",
    "TTS/Operador Logístico e TTS/Industria"
]

coluna_1_fisc = [
    "Escrituração de Notas Fiscais de Entrada",
    "Escrituração de Notas Fiscais de Saída",
    "Escrituração de Notas de Serviços Prestados",
    "Escrituração de Notas de Serviços Tomados",
    "Emissão de notas fiscais de serviços",
    "Emissão de notas fiscais eletrônicas de produtos",
    "ICMS Incentivado"
]

coluna_2_fisc = [
    "Apuração: DAS",
    "Apuração: ICMS",
    "Apuração: ICMS-ST",
    "Apuração: ISS",
    "Apuração: PIS",
    "Apuração: COFINS"
]

coluna_3_fisc = [
    "Apuração: IRPJ",
    "Apuração: CSLL",
    "Apuração: IPI",
    "Apuração: IRRF",
    "Apuração: CSRF",
    "Apuração: INSS Retido"
]

coluna_4_fisc = [
    "Entrega: DCTFWeb",
    "Entrega: SPED Fiscal",
    "Entrega: SPED Contribuições",
    "Entrega: DEFIS",
    "Entrega: PGDAS-D",
    "Entrega: GIA / GIA-ST",
    "Entrega: SINTEGRA",
    "Consultas Tributárias",
    "Dúvidas Tributárias",
    "Acompanhamento de CND Federal",
    "Acompanhamento de CND Estadual",
    "Acompanhamento de CND Municipal",
    "Atendimento a fiscalizações e malhas fiscais",
    "Recálculo de Guias",
    "Recálculo de Parcelamentos",
    "Simulação de Parcelamentos"
]

itens_fiscais = coluna_1_fisc + coluna_2_fisc + coluna_3_fisc + coluna_4_fisc

itens_contabeis = [
    "Processamento e Conciliação Bancária",
    "Elaboração de Balancetes Mensais/Trimestrais",
    "Balanço Patrimonial (BP)",
    "Demonstração do Resultado do Exercício (DRE)",
    "Demonstração dos Lucros ou Prejuízos Acumulados (DLPA)",
    "Demonstração das Mutações do Patrimônio Líquido (DMPL)",
    "Demonstração dos Fluxos de Caixa (DFC)",
    "Demonstração do Valor Adicionado (DVA)",
    "Elaboração de Notas Explicativas",
    "Entrega de SPED Contábil (ECD)",
    "Entrega de ECF",
    "Apuração de IRPJ e CSLL Lucro Real (Trimestral)",
    "Apuração de IRPJ e CSLL Lucro Real (Anual)"
]

itens_dp = [
    "Processamento de Folha de Pagamento Mensal",
    "Processamento de Adiantamento Salarial",
    "Processamento de Pró-labore",
    "Processamento de 13º Salário",
    "Gestão de Férias",
    "Gestão de Admissões",
    "Gestão de Rescisões",
    "Transmissão de eventos para o eSocial",
    "Entrega: EFD-Reinf",
    "Entrega: DCTFWeb",
    "Apuração de INSS (DARF Previdenciário)",
    "Apuração de FGTS",
    "Apuração de IRRF sobre folha",
    "Entrega de DIRF",
    "Emissão de Informe de Rendimentos",
    "Gestão de Parcelamentos",
    "Controle de Empréstimos Consignados"
]

def toggle_all_fiscal():
    check = st.session_state.chk_all_fiscal
    for i, item in enumerate(itens_fiscais):
        st.session_state[f"fisc_{i}"] = check
        st.session_state.form_data["escopo_fiscal"][item] = check

def toggle_all_contabil():
    check = st.session_state.chk_all_contabil
    for i, item in enumerate(itens_contabeis):
        st.session_state[f"cont_{i}"] = check
        st.session_state.form_data["escopo_contabil"][item] = check

def toggle_all_dp():
    check = st.session_state.chk_all_dp
    for i, item in enumerate(itens_dp):
        st.session_state[f"dp_{i}"] = check
        st.session_state.form_data["escopo_dp"][item] = check

def update_cb_fiscal(i, item):
    st.session_state.form_data["escopo_fiscal"][item] = st.session_state[f"fisc_{i}"]

def update_cb_contabil(i, item):
    st.session_state.form_data["escopo_contabil"][item] = st.session_state[f"cont_{i}"]

def update_cb_dp(i, item):
    st.session_state.form_data["escopo_dp"][item] = st.session_state[f"dp_{i}"]

# Forçar a inicialização das chaves no session_state para evitar KeyError ao carregar draft
for i, item in enumerate(itens_fiscais):
    if f"fisc_{i}" not in st.session_state:
        st.session_state[f"fisc_{i}"] = st.session_state.form_data["escopo_fiscal"].get(item, False)
        
for i, item in enumerate(itens_contabeis):
    if f"cont_{i}" not in st.session_state:
        st.session_state[f"cont_{i}"] = st.session_state.form_data["escopo_contabil"].get(item, False)
        
for i, item in enumerate(itens_dp):
    if f"dp_{i}" not in st.session_state:
        st.session_state[f"dp_{i}"] = st.session_state.form_data["escopo_dp"].get(item, False)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏢 Dados Cadastrais", 
    "📞 Contatos", 
    "📊 Fiscal & Contábil", 
    "👥 DP & Regularização", 
    "✅ Resumo e Gerar PDF"
])

with tab1:
    st.subheader("Dados Cadastrais")
    c1, c2, c3 = st.columns([1, 1, 2])
    
    st.session_state.form_data["cnpj"] = c1.text_input("CNPJ", value=st.session_state.form_data.get("cnpj", ""))
    st.session_state.form_data["ie"] = c2.text_input("Inscrição Estadual Principal", value=st.session_state.form_data.get("ie", ""))
    st.session_state.form_data["razao_social"] = c3.text_input("Razão Social", value=st.session_state.form_data.get("razao_social", ""))
    
    c4, c5 = st.columns([2, 1])
    st.session_state.form_data["nome_fantasia"] = c4.text_input("Nome Fantasia", value=st.session_state.form_data.get("nome_fantasia", ""))
    st.session_state.form_data["data_abertura"] = c5.text_input("Data de Abertura", value=st.session_state.form_data.get("data_abertura", ""))
    
    st.session_state.form_data["cnae_principal"] = st.text_input("CNAE Principal", value=st.session_state.form_data.get("cnae_principal", ""))
    st.session_state.form_data["endereco"] = st.text_input("Endereço Completo", value=st.session_state.form_data.get("endereco", ""))
    
    st.divider()
    st.subheader("Informações do Contrato")
    c6, c7 = st.columns(2)
    st.session_state.form_data["data_inicio_cliente"] = c6.text_input("Cliente a partir de (Mês/Ano)", value=st.session_state.form_data.get("data_inicio_cliente", ""))
    idx_regime = REGIMES.index(st.session_state.form_data.get("regime_tributario", "Simples Nacional")) if st.session_state.form_data.get("regime_tributario") in REGIMES else 1
    st.session_state.form_data["regime_tributario"] = c7.selectbox("Regime Tributário", REGIMES, index=idx_regime)

with tab2:
    st.subheader("Contatos dos Responsáveis")
    contatos_atuais = st.session_state.form_data.get("contatos", [])
    if not contatos_atuais:
        contatos_atuais = [{"Nome": "", "Setor": "Sócio/Diretor", "E-mail": "", "WhatsApp": ""}]
    
    df_contatos = pd.DataFrame(contatos_atuais)
    edited_df = st.data_editor(
        df_contatos,
        num_rows="dynamic",
        column_config={
            "Setor": st.column_config.SelectboxColumn(
                "Setor", help="Selecione o setor", options=SETORES, required=True
            )
        },
        use_container_width=True
    )
    st.session_state.form_data["contatos"] = edited_df.to_dict('records')

with tab3:
    st.subheader("Escopo: Compliance Fiscal")
    all_checked_fiscal = all(st.session_state.form_data["escopo_fiscal"].get(item, False) for item in itens_fiscais) if st.session_state.form_data["escopo_fiscal"] else False
    st.checkbox("Selecionar Todos (Compliance Fiscal)", value=all_checked_fiscal, key="chk_all_fiscal", on_change=toggle_all_fiscal)
    st.write("")
    
    cols_fiscal = st.columns(4)
    listas_colunas_fiscais = [coluna_1_fisc, coluna_2_fisc, coluna_3_fisc, coluna_4_fisc]
    
    for col_idx, lista in enumerate(listas_colunas_fiscais):
        with cols_fiscal[col_idx]:
            for item in lista:
                i = itens_fiscais.index(item)
                
                # O checkbox usando a chave direta do session state e on_change
                st.checkbox(item, key=f"fisc_{i}", on_change=update_cb_fiscal, args=(i, item))
                
                # Se estiver marcado, mostra o input dependente
                if st.session_state[f"fisc_{i}"]:
                    if item == "Escrituração de Notas Fiscais de Entrada":
                        val = st.session_state.form_data.get("qtd_notas_entrada", "")
                        st.session_state.form_data["qtd_notas_entrada"] = st.text_input("Qtd média Entradas", value=val, key="in_qtd_ent")
                    elif item == "Escrituração de Notas Fiscais de Saída":
                        val = st.session_state.form_data.get("qtd_notas_saida", "")
                        st.session_state.form_data["qtd_notas_saida"] = st.text_input("Qtd média Saídas", value=val, key="in_qtd_sai")
                    elif item == "Emissão de notas fiscais de serviços":
                        val = st.session_state.form_data.get("qtd_emissao_notas_servico", "")
                        st.session_state.form_data["qtd_emissao_notas_servico"] = st.text_input("Qtd Emissão Serviços", value=val, key="in_qtd_emis_serv")
                    elif item == "Emissão de notas fiscais eletrônicas de produtos":
                        val = st.session_state.form_data.get("qtd_emissao_notas_produto", "")
                        st.session_state.form_data["qtd_emissao_notas_produto"] = st.text_input("Qtd Emissão Produtos", value=val, key="in_qtd_emis_prod")
                    elif item == "ICMS Incentivado":
                        selecionados = st.multiselect(
                            "Selecione os incentivos (TTS):",
                            options=OPCOES_TTS,
                            default=st.session_state.form_data.get("tipos_icms_incentivado", [])
                        )
                        st.session_state.form_data["tipos_icms_incentivado"] = selecionados
                    elif item == "Apuração: ICMS-ST":
                        estados_selecionados = st.multiselect(
                            "Estados ICMS-ST:",
                            options=ESTADOS,
                            default=st.session_state.form_data.get("estados_icms_st", [])
                        )
                        st.session_state.form_data["estados_icms_st"] = estados_selecionados

    st.divider()
    st.subheader("Escopo: Contabilidade")
    all_checked_cont = all(st.session_state.form_data["escopo_contabil"].get(item, False) for item in itens_contabeis) if st.session_state.form_data["escopo_contabil"] else False
    st.checkbox("Selecionar Todos (Contabilidade)", value=all_checked_cont, key="chk_all_contabil", on_change=toggle_all_contabil)
    st.write("")
    
    col_c1, col_c2 = st.columns(2)
    for i, item in enumerate(itens_contabeis):
        col = col_c1 if i % 2 == 0 else col_c2
        col.checkbox(item, key=f"cont_{i}", on_change=update_cb_contabil, args=(i, item))


with tab4:
    st.subheader("Escopo: Departamento Pessoal")
    all_checked_dp = all(st.session_state.form_data["escopo_dp"].get(item, False) for item in itens_dp) if st.session_state.form_data["escopo_dp"] else False
    st.checkbox("Selecionar Todos (Departamento Pessoal)", value=all_checked_dp, key="chk_all_dp", on_change=toggle_all_dp)
    st.write("")
    
    col_d1, col_d2 = st.columns(2)
    for i, item in enumerate(itens_dp):
        col = col_d1 if i % 2 == 0 else col_d2
        col.checkbox(item, key=f"dp_{i}", on_change=update_cb_dp, args=(i, item))

    st.divider()
    st.subheader("Escopo: Regularização / Abertura")
    itens_reg = [
        "Elaboração de Contrato Social e Viabilidade",
        "Alteração Contratual",
        "Inscrição no CNPJ",
        "Inscrição Estadual",
        "Inscrição Municipal",
        "Obtenção de Alvará de Funcionamento",
        "Corpo de Bombeiros (AVCB/CLCB)",
        "Vigilância Sanitária",
        "IBAMA (CTF)",
        "Inscrições de Substituto Tributário (ST)"
    ]
    
    for i, item in enumerate(itens_reg):
        valor_atual = st.session_state.form_data["escopo_regularizacao"].get(item, False)
        marcado = st.checkbox(item, value=valor_atual, key=f"reg_{i}")
        st.session_state.form_data["escopo_regularizacao"][item] = marcado
        
        # Lógica especial para ST
        if item == "Inscrições de Substituto Tributário (ST)" and marcado:
            estados_selecionados = st.multiselect(
                "Selecione os Estados para Inscrição ST:",
                options=ESTADOS,
                default=st.session_state.form_data.get("estados_st", [])
            )
            st.session_state.form_data["estados_st"] = estados_selecionados

with tab5:
    st.subheader("Resumo do Cliente")
    st.session_state.form_data["resumo_cliente"] = st.text_area(
        "Escreva um breve resumo da empresa, histórico, segmento ou pontos de atenção:",
        value=st.session_state.form_data.get("resumo_cliente", ""),
        height=150
    )
    
    st.divider()
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        if st.button("💾 Salvar Rascunho no Banco", use_container_width=True):
            cnpj_save = st.session_state.form_data.get("cnpj")
            razao_save = st.session_state.form_data.get("razao_social")
            if not cnpj_save:
                st.error("Preencha o CNPJ antes de salvar.")
            else:
                save_client_data(cnpj_save, razao_save, st.session_state.form_data)
                st.success("Dados salvos com sucesso!")
                
    with col_btn2:
        if st.button("📄 Gerar Ficha em PDF", use_container_width=True):
            cnpj_save = st.session_state.form_data.get("cnpj")
            if not cnpj_save:
                st.error("Preencha o CNPJ antes de gerar o PDF.")
            else:
                save_client_data(cnpj_save, st.session_state.form_data.get("razao_social", ""), st.session_state.form_data)
                
                pdf_path = f"ficha_cliente_{cnpj_save}.pdf"
                gerar_pdf(st.session_state.form_data, pdf_path)
                
                with open(pdf_path, "rb") as pdf_file:
                    st.download_button(
                        label="⬇️ Download do PDF Gerado",
                        data=pdf_file,
                        file_name=pdf_path,
                        mime="application/pdf",
                        use_container_width=True
                    )
                st.success("PDF gerado! Clique no botão acima para baixar.")
