from fpdf import FPDF
import datetime

class FichaClientePDF(FPDF):
    def header(self):
        # Logo / Title
        self.set_font("helvetica", "B", 16)
        self.cell(0, 10, "NASCEL - CONTABILIDADE", border=0, ln=1, align="C")
        self.set_font("helvetica", "B", 12)
        self.cell(0, 10, "FICHA DE NOVO CLIENTE", border=0, ln=1, align="C")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.cell(0, 10, f"Página {self.page_no()}/{{nb}}", 0, 0, "C")

    def desenhar_titulo_bloco(self, titulo):
        self.set_font("helvetica", "B", 10)
        self.set_fill_color(200, 220, 255)
        self.cell(0, 8, titulo, border=1, ln=1, align="L", fill=True)

    def desenhar_linha_chave_valor(self, chave, valor, largura_chave=50, altura=6, ln=1):
        self.set_font("helvetica", "B", 9)
        self.cell(largura_chave, altura, f"{chave}:", border="L", ln=0)
        self.set_font("helvetica", "", 9)
        # remove quebras de linha ou trata multi_cell se necessario
        valor_str = str(valor) if valor else "N/A"
        # Para caber em uma linha, usaremos substring ou a impressao na mesma linha
        # Se for a ultima coluna da linha, desenhamos a borda direita "R" tambem
        borda_direita = "R" if ln == 1 else ""
        largura_valor = self.epw - largura_chave if ln == 1 else 0
        self.cell(largura_valor, altura, valor_str, border=borda_direita, ln=ln)

    def desenhar_texto_longo(self, texto):
        self.set_font("helvetica", "", 9)
        if not texto:
            texto = "N/A"
        self.multi_cell(0, 6, texto, border=1)

    def add_bloco_cadastral(self, dados):
        self.desenhar_titulo_bloco("1. DADOS CADASTRAIS")
        
        self.set_font("helvetica", "B", 9)
        self.cell(20, 6, "CNPJ:", border="L", ln=0)
        self.set_font("helvetica", "", 9)
        self.cell(40, 6, str(dados.get("cnpj", "")), border=0, ln=0)

        self.set_font("helvetica", "B", 9)
        self.cell(10, 6, "IE:", border=0, ln=0)
        self.set_font("helvetica", "", 9)
        self.cell(30, 6, str(dados.get("ie", "")), border=0, ln=0)
        
        self.set_font("helvetica", "B", 9)
        self.cell(20, 6, "Abertura:", border=0, ln=0)
        self.set_font("helvetica", "", 9)
        self.cell(0, 6, str(dados.get("data_abertura", "")), border="R", ln=1)
        
        self.desenhar_linha_chave_valor("Razão Social", dados.get("razao_social", ""))
        self.desenhar_linha_chave_valor("Nome Fantasia", dados.get("nome_fantasia", ""))
        self.desenhar_linha_chave_valor("CNAE Principal", dados.get("cnae_principal", ""))
        self.desenhar_linha_chave_valor("Endereço", dados.get("endereco", ""))
        self.desenhar_linha_chave_valor("Início Cliente em", dados.get("data_inicio_cliente", ""))
        
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
        self.cell(50, 6, "Nome", border=1, ln=0)
        self.cell(40, 6, "Setor", border=1, ln=0)
        self.cell(60, 6, "E-mail", border=1, ln=0)
        self.cell(0, 6, "WhatsApp", border=1, ln=1)
        
        self.set_font("helvetica", "", 9)
        for contato in tabela_contatos:
            self.cell(50, 6, str(contato.get("Nome", "")), border=1, ln=0)
            self.cell(40, 6, str(contato.get("Setor", "")), border=1, ln=0)
            self.cell(60, 6, str(contato.get("E-mail", "")), border=1, ln=0)
            self.cell(0, 6, str(contato.get("WhatsApp", "")), border=1, ln=1)
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
                self.set_text_color(0, 51, 153)
                self.cell(0, 8, categoria.upper(), border=0, ln=1)
                self.set_text_color(0, 0, 0)
                
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
                    
                    self.multi_cell(0, 6, f"[X] {item}{texto_extra}")
                self.ln(4)

def gerar_pdf(dados_form, filepath):
    pdf = FichaClientePDF()
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
