from fpdf import FPDF
from datetime import datetime
import os

LARANJA_NASCEL = (252, 164, 34)  # #fca422
CINZA_NASCEL = (116, 106, 105)   # #746a69
BRANCO = (255, 255, 255)         # #ffffff
CINZA_TEXTO = (72, 66, 65)
CINZA_LINHA = (215, 210, 209)
FUNDO_SUAVE = (250, 247, 243)

def formatar_data_br(valor):
    if not valor:
        return "Não informado"
    texto = str(valor).strip()
    for formato in ("%Y-%m-%d", "%d/%m/%Y", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(texto, formato).strftime("%d/%m/%Y")
        except ValueError:
            continue
    return texto

def formatar_cnpj(valor):
    digitos = "".join(filter(str.isdigit, str(valor or "")))
    if len(digitos) == 14:
        return f"{digitos[:2]}.{digitos[2:5]}.{digitos[5:8]}/{digitos[8:12]}-{digitos[12:]}"
    return str(valor or "Não informado")

def formatar_periodo(valor):
    digitos = "".join(filter(str.isdigit, str(valor or "")))[:6]
    if len(digitos) == 6:
        return f"{digitos[:2]}/{digitos[2:]}"
    return str(valor or "Não informado")

def formatar_telefone(valor):
    digitos = "".join(filter(str.isdigit, str(valor or "")))
    if len(digitos) in (12, 13) and digitos.startswith("55"):
        digitos = digitos[2:]
    if len(digitos) == 11:
        return f"({digitos[:2]}) {digitos[2:7]}-{digitos[7:]}"
    if len(digitos) == 10:
        return f"({digitos[:2]}) {digitos[2:6]}-{digitos[6:]}"
    return str(valor or "Não informado")

class FichaClientePDF(FPDF):
    def __init__(self, logo_path=None):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.logo_path = logo_path if logo_path and os.path.exists(logo_path) else None
        self.set_margins(14, 18, 14)
        self.set_auto_page_break(auto=True, margin=18)

    def header(self):
        if self.logo_path:
            self.image(self.logo_path, x=self.l_margin, y=9, w=43)
            texto_x = self.l_margin + 49
        else:
            self.set_fill_color(*LARANJA_NASCEL)
            self.rect(self.l_margin, 8, 38, 14, style="F")
            self.set_xy(self.l_margin, 10)
            self.set_text_color(*BRANCO)
            self.set_font("helvetica", "B", 15)
            self.cell(38, 9, "NASCEL", align="C")
            texto_x = self.l_margin + 44

        self.set_xy(texto_x, 8)
        self.set_text_color(*CINZA_NASCEL)
        self.set_font("helvetica", "B", 13)
        self.cell(0, 7, "FICHA DE NOVO CLIENTE", ln=1)
        self.set_x(texto_x)
        self.set_text_color(*CINZA_TEXTO)
        self.set_font("helvetica", "", 8)
        self.cell(0, 5, "NASCEL CONTABILIDADE E ASSESSORIA", ln=1)
        self.set_draw_color(*LARANJA_NASCEL)
        self.set_line_width(0.8)
        self.line(self.l_margin, 25, self.w - self.r_margin, 25)
        self.set_y(30)

    def footer(self):
        self.set_y(-15)
        self.set_draw_color(*CINZA_LINHA)
        self.set_line_width(0.2)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.set_y(-13)
        self.set_text_color(*CINZA_TEXTO)
        self.set_font("helvetica", "I", 8)
        self.cell(self.epw / 2, 7, "Documento interno - Nascel", 0, 0, "L")
        self.cell(self.epw / 2, 7, f"Página {self.page_no()}/{{nb}}", 0, 0, "R")

    def desenhar_titulo_bloco(self, titulo):
        self.set_text_color(*CINZA_TEXTO)
        self.set_font("helvetica", "B", 10)
        self.set_fill_color(*FUNDO_SUAVE)
        self.set_draw_color(*CINZA_LINHA)
        x, y = self.get_x(), self.get_y()
        self.cell(0, 8, f"    {titulo}", border=0, ln=1, align="L", fill=True)
        self.set_fill_color(*LARANJA_NASCEL)
        self.rect(x, y, 2.2, 8, style="F")
        self.set_text_color(*CINZA_TEXTO)

    def desenhar_linha_chave_valor(self, chave, valor, largura_chave=50, altura=6, ln=1):
        self.set_draw_color(*CINZA_LINHA)
        self.set_font("helvetica", "B", 8.5)
        self.cell(largura_chave, altura, f"{chave}:", border="L", ln=0, fill=False)
        self.set_font("helvetica", "", 9)
        # remove quebras de linha ou trata multi_cell se necessario
        valor_str = str(valor) if valor else "Não informado"
        # Para caber em uma linha, usaremos substring ou a impressao na mesma linha
        # Se for a ultima coluna da linha, desenhamos a borda direita "R" tambem
        borda_direita = "R" if ln == 1 else ""
        largura_valor = self.epw - largura_chave if ln == 1 else 0
        self.cell(largura_valor, altura, valor_str, border=borda_direita, ln=ln)

    def desenhar_texto_longo(self, texto):
        self.set_font("helvetica", "", 9)
        if not texto:
            texto = "Não informado"
        self.multi_cell(0, 6, texto, border=1)

    def add_bloco_cadastral(self, dados):
        self.desenhar_titulo_bloco("1. DADOS CADASTRAIS")
        
        self.set_font("helvetica", "B", 9)
        self.cell(20, 6, "CNPJ:", border="L", ln=0)
        self.set_font("helvetica", "", 9)
        self.cell(40, 6, formatar_cnpj(dados.get("cnpj", "")), border=0, ln=0)

        self.set_font("helvetica", "B", 9)
        self.cell(10, 6, "IE:", border=0, ln=0)
        self.set_font("helvetica", "", 9)
        self.cell(30, 6, str(dados.get("ie", "")), border=0, ln=0)
        
        self.set_font("helvetica", "B", 9)
        self.cell(20, 6, "Abertura:", border=0, ln=0)
        self.set_font("helvetica", "", 9)
        self.cell(0, 6, formatar_data_br(dados.get("data_abertura", "")), border="R", ln=1)
        
        self.desenhar_linha_chave_valor("Razão Social", dados.get("razao_social", ""))
        self.desenhar_linha_chave_valor("Nome Fantasia", dados.get("nome_fantasia", ""))
        self.desenhar_linha_chave_valor("CNAE Principal", dados.get("cnae_principal", ""))
        self.desenhar_linha_chave_valor("Endereço", dados.get("endereco", ""))
        self.desenhar_linha_chave_valor("Início Cliente em", formatar_periodo(dados.get("data_inicio_cliente", "")))
        
        # Borda inferior
        self.cell(0, 0, "", border="T", ln=1)
        self.ln(3)

    def add_bloco_tributacao(self, dados):
        self.desenhar_titulo_bloco("2. TRIBUTAÇÃO E ATIVIDADE")
        self.desenhar_linha_chave_valor("Regime Tributário", dados.get("regime_tributario", ""))
        self.cell(0, 0, "", border="T", ln=1)
        self.ln(3)

    def add_bloco_contatos(self, tabela_contatos):
        self.desenhar_titulo_bloco("3. CONTATOS DOS RESPONSÁVEIS")
        if not tabela_contatos:
            self.cell(0, 6, "Nenhum contato adicionado.", border=1, ln=1)
            self.ln(3)
            return

        # Cabeçalho tabela
        self.set_font("helvetica", "B", 9)
        self.set_fill_color(*CINZA_NASCEL)
        self.set_text_color(*BRANCO)
        self.cell(43, 7, "Nome", border=1, ln=0, fill=True)
        self.cell(31, 7, "Setor", border=1, ln=0, fill=True)
        self.cell(52, 7, "E-mail", border=1, ln=0, fill=True)
        self.cell(34, 7, "Telefone", border=1, ln=0, fill=True)
        self.cell(0, 7, "WhatsApp", border=1, ln=1, fill=True)
        
        self.set_text_color(*CINZA_TEXTO)
        self.set_font("helvetica", "", 9)
        for contato in tabela_contatos:
            whatsapp = contato.get("WhatsApp", False)
            telefone = contato.get("Telefone", "")
            if not telefone and isinstance(whatsapp, str):
                telefone = whatsapp
                whatsapp = bool(whatsapp.strip())
            self.cell(43, 7, str(contato.get("Nome", ""))[:25], border=1, ln=0)
            self.cell(31, 7, str(contato.get("Setor", ""))[:18], border=1, ln=0)
            self.cell(52, 7, str(contato.get("E-mail", ""))[:31], border=1, ln=0)
            self.cell(34, 7, formatar_telefone(telefone)[:20], border=1, ln=0)
            self.cell(0, 7, "Sim" if whatsapp else "Não", border=1, ln=1, align="C")
        self.ln(3)

    def add_bloco_resumo_escopo(self, dict_escopo_macro):
        self.desenhar_titulo_bloco("4. RESUMO DO ESCOPO CONTRATADO")
        self.set_font("helvetica", "", 9)
        marcados = [k for k, v in dict_escopo_macro.items() if v]
        if not marcados:
            self.cell(0, 6, "Nenhum serviço macro selecionado.", border=1, ln=1)
        else:
            texto = ", ".join(marcados)
            self.multi_cell(0, 6, texto, border=1)
        self.ln(3)

    def add_bloco_resumo_cliente(self, texto):
        self.desenhar_titulo_bloco("5. RESUMO / HISTÓRICO DO CLIENTE")
        self.desenhar_texto_longo(texto)
        self.ln(5)

    def add_anexo_detalhado(self, escopos_detalhados, dados_form):
        for categoria, itens in escopos_detalhados.items():
            marcados = [k for k, v in itens.items() if v]
            if marcados:
                self.add_page()
                self.set_font("helvetica", "B", 12)
                self.cell(0, 10, f"ANEXO I - DETALHAMENTO DO ESCOPO ({categoria.upper()})", border=0, ln=1, align="C")
                self.ln(5)

                self.set_font("helvetica", "B", 10)
                self.set_text_color(*CINZA_NASCEL)
                self.cell(0, 8, categoria.upper(), border=0, ln=1)
                self.set_text_color(*CINZA_TEXTO)
                
                self.set_font("helvetica", "", 9)
                for item in marcados:
                    self.set_x(self.l_margin + 5) # recuo fixo
                    texto_extra = ""
                    if item == "Inscrições de Substituto Tributário (ST)" and dados_form.get("estados_st"):
                        texto_extra = f" - Estados: {', '.join(dados_form.get('estados_st', []))}"
                    elif item == "Apuração: ICMS-ST" and dados_form.get("estados_icms_st"):
                        texto_extra = f" - Estados: {', '.join(dados_form.get('estados_icms_st', []))}"
                    elif item == "Escrituração de Notas Fiscais de Entrada" and dados_form.get("qtd_notas_entrada"):
                        texto_extra = f" (Quantidade Média: {dados_form.get('qtd_notas_entrada')}/mês)"
                    elif item == "Escrituração de Notas Fiscais de Saída" and dados_form.get("qtd_notas_saida"):
                        texto_extra = f" (Quantidade Média: {dados_form.get('qtd_notas_saida')}/mês)"
                    elif item == "Emissão de notas fiscais de serviços" and dados_form.get("qtd_emissao_notas_servico"):
                        texto_extra = f" (Quantidade Média: {dados_form.get('qtd_emissao_notas_servico')}/mês)"
                    elif item == "Emissão de notas fiscais eletrônicas de produtos" and dados_form.get("qtd_emissao_notas_produto"):
                        texto_extra = f" (Quantidade Média: {dados_form.get('qtd_emissao_notas_produto')}/mês)"
                    elif item == "ICMS Incentivado" and dados_form.get("tipos_icms_incentivado"):
                        texto_extra = f" - Opções: {', '.join(dados_form.get('tipos_icms_incentivado', []))}"
                    
                    self.set_text_color(*LARANJA_NASCEL)
                    self.cell(6, 6, "[x]", ln=0)
                    self.set_text_color(*CINZA_TEXTO)
                    self.multi_cell(0, 6, f"{item}{texto_extra}")
                self.ln(4)

def gerar_pdf(dados_form, filepath, logo_path=None):
    if logo_path is None:
        pasta_assets = os.path.join(os.path.dirname(__file__), "assets")
        candidatos = [
            os.path.join(pasta_assets, "logo_nascel.png"),
            os.path.join(pasta_assets, "logo_nascel.jpg"),
            os.path.join(pasta_assets, "logo_nascel.jpeg"),
        ]
        logo_path = next((caminho for caminho in candidatos if os.path.exists(caminho)), None)
    pdf = FichaClientePDF(logo_path=logo_path)
    pdf.alias_nb_pages()
    pdf.add_page()
    
    pdf.add_bloco_cadastral(dados_form)
    pdf.add_bloco_tributacao(dados_form)
    pdf.add_bloco_contatos(dados_form.get("contatos", []))
    
    # Extrair macros
    macros = {
        "Compliance Fiscal": any(dados_form.get("escopo_fiscal", {}).values()),
        "Contabilidade": any(dados_form.get("escopo_contabil", {}).values()),
        "Departamento Pessoal": any(dados_form.get("escopo_dp", {}).values()),
        "Abertura / Regularização": any(dados_form.get("escopo_regularizacao", {}).values())
    }
    pdf.add_bloco_resumo_escopo(macros)
    pdf.add_bloco_resumo_cliente(dados_form.get("resumo_cliente", ""))
    
    # Anexo Detalhado
    escopos = {
        "Compliance Fiscal": dados_form.get("escopo_fiscal", {}),
        "Contabilidade": dados_form.get("escopo_contabil", {}),
        "Departamento Pessoal": dados_form.get("escopo_dp", {}),
        "Regularização / Abertura": dados_form.get("escopo_regularizacao", {})
    }
    # Verifica se tem pelo menos 1 item marcado no anexo
    tem_anexo = False
    for k, v in escopos.items():
        if any(v.values()):
            tem_anexo = True
            break
            
    if tem_anexo:
        pdf.add_anexo_detalhado(escopos, dados_form)
    
    pdf.output(filepath)
    return filepath
