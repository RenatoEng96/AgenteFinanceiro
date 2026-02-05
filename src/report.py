import re
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.units import cm

def gerar_pdf_v11(dados, valuation, comparables, parecer_texto, perfil_empresa):
    try:
        nome_arquivo = f"Relatorio_Deep_Analysis_{dados.get('ticker', 'UNKNOWN')}_{datetime.now().strftime('%Y%m%d')}.pdf"
        doc = SimpleDocTemplate(nome_arquivo, pagesize=A4, rightMargin=1.5*cm, leftMargin=1.5*cm, topMargin=1.5*cm, bottomMargin=1.5*cm)
        styles = getSampleStyleSheet()
        story = []

        # --- ESTILOS PERSONALIZADOS ---
        style_title = ParagraphStyle('CT', parent=styles['Title'], fontSize=20, textColor=colors.HexColor("#1A237E"), spaceAfter=12)
        style_subtitle = ParagraphStyle('ST', parent=styles['Normal'], fontSize=12, textColor=colors.grey, spaceAfter=20)
        style_h1 = ParagraphStyle('H1', parent=styles['Heading1'], fontSize=14, textColor=colors.HexColor("#0D47A1"), spaceBefore=15, spaceAfter=10, borderPadding=5, backColor=colors.HexColor("#E3F2FD"))
        style_h2 = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=12, textColor=colors.black, spaceBefore=10)
        style_normal = ParagraphStyle('CN', parent=styles['Normal'], fontSize=10, leading=12, alignment=4) 
        style_destaque_box = ParagraphStyle('Box', parent=styles['Normal'], fontSize=10, backColor=colors.HexColor("#FFF3E0"), borderPadding=8, borderColor=colors.orange, borderWidth=1)
        style_small = ParagraphStyle('Small', parent=styles['Normal'], fontSize=8, textColor=colors.grey)

        # --- CABEÇALHO ---
        story.append(Paragraph(f"Relatório de Análise Profunda: {dados.get('ticker')}", style_title))
        story.append(Paragraph(f"Empresa: {dados.get('nome')} | Setor: {dados.get('setor')} | Data: {datetime.now().strftime('%d/%m/%Y')}", style_subtitle))
        
        texto_perfil = f"<b>Perfil Estratégico Identificado:</b> {perfil_empresa}"
        story.append(Paragraph(texto_perfil, style_destaque_box))
        story.append(Spacer(1, 0.5*cm))

        # --- 1. DASHBOARD FUNDAMENTALISTA ---
        story.append(Paragraph("1. Dashboard de Fundamentos e Qualidade", style_h1))
        
        def fmt(val, sulfixo="", multiplicador=1):
            if val is None or val == "": return "-"
            try:
                return f"{float(val)*multiplicador:.2f}{sulfixo}"
            except: return str(val)

        cotacao = dados.get('cotacao')
        pl = dados.get('pl')
        dy = dados.get('dy_anual')
        pvp = dados.get('pvp')
        roe = dados.get('roe')
        ev_ebitda = dados.get('ev_ebitda')
        margem_liq = dados.get('margem_liq')
        div_liq_ebitda = dados.get('divida_liquida_ebitda')
        div_liq_acao = dados.get('divida_liquida_por_acao')

        data_fund = [
            ["Cotação Atual", f"R$ {fmt(cotacao, '', 1)}", "P/L (Preço/Lucro)", fmt(pl, "x")],
            ["Dividend Yield (12m)", fmt(dy, "%", 100), "P/VP (Preço/Valor Patr.)", fmt(pvp, "x")],
            ["ROE (Retorno s/ PL)", fmt(roe, "%", 100), "EV / EBITDA", fmt(ev_ebitda, "x")],
            ["Margem Líquida", fmt(margem_liq, "%", 100), "Dívida Líq. / EBITDA", fmt(div_liq_ebitda, "x")]
        ]
        
        if data_fund[3][3] == "-":
            data_fund[3][2] = "Dívida Líq./Ação"
            data_fund[3][3] = f"R$ {fmt(div_liq_acao, '', 1)}"

        t_fund = Table(data_fund, colWidths=[4*cm, 4*cm, 4*cm, 4*cm])
        t_fund.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('BACKGROUND', (0,0), (0,-1), colors.HexColor("#F5F5F5")),
            ('BACKGROUND', (2,0), (2,-1), colors.HexColor("#F5F5F5")),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        story.append(t_fund)
        
        if 'moat_score' in dados:
            story.append(Spacer(1, 0.2*cm))
            story.append(Paragraph(f"<b>Economic Moat Score (IA):</b> {dados.get('moat_score')}/10 - {dados.get('moat_justificativa')}", style_normal))
        
        story.append(Spacer(1, 0.5*cm))

        # --- 2. TRIANGULAÇÃO DE VALUATION ---
        story.append(Paragraph("2. Modelagem de Valor Intrínseco", style_h1))

        # Recuperação segura dos objetos
        dcf = valuation.get('DCF_Adaptativo', {}) or {}
        rev_dcf = valuation.get('Reverse_DCF', {}) # Pode ser None se for banco
        graham = valuation.get('Graham', {}) or {}
        bazin = valuation.get('Bazin', {}) or {}
        lynch = valuation.get('Peter_Lynch', {}) or {}
        
        # --- EXIBIÇÃO DA LÓGICA MACRO ---
        premissas = dcf.get('Premissas', {})
        # Pode ser WACC (Indústria) ou Ke (Bancos)
        taxa_usada = premissas.get('WACC') or premissas.get('Ke (Custo)', 'N/A')
        
        story.append(Paragraph(f"<b>Premissas Macro-Dinâmicas (CAPM):</b>", style_normal))
        explicacao_wacc = f"""
        A Taxa de Desconto utilizada de <b>{taxa_usada}</b> foi calculada dinamicamente via CAPM 
        (Taxa Livre de Risco + Beta x Equity Risk Premium).
        """
        story.append(Paragraph(explicacao_wacc, style_small))
        story.append(Spacer(1, 0.2*cm))

        # Tabela de Valuation
        data_val = [["Metodologia", "Foco", "Preço Justo", "Upside", "Veredito"]]

        def get_color(margem):
            if margem == 'N/A' or margem == '-': return colors.black
            try:
                m = float(margem)
                return colors.green if m > 0 else colors.red
            except: return colors.black

        # DCF ou MODELO DE DIVIDENDOS (Depende do que veio na chave 'Tipo')
        label_principal = dcf.get('Tipo', 'DCF (Fluxo de Caixa)')
        margem_dcf = dcf.get('Margem', 0)
        data_val.append([
            label_principal, "Longo Prazo", f"R$ {dcf.get('Valor', 0)}", f"{margem_dcf}%", 
            "Descontado" if isinstance(margem_dcf, (int, float)) and margem_dcf > 0 else "Prêmio"
        ])
        
        # Graham
        if graham.get('Valor', 0) > 0:
            margem_g = graham.get('Margem', 0)
            data_val.append([
                "Graham (Clássico)", "Patrimonial", f"R$ {graham.get('Valor')}", f"{margem_g}%", 
                "Descontado" if isinstance(margem_g, (int, float)) and margem_g > 0 else "Caro"
            ])
            
        # Bazin
        if bazin.get('Preco_Teto', 0) > 0:
            margem_b = bazin.get('Margem', 0)
            data_val.append([
                "Décio Bazin", "Dividendos", f"R$ {bazin.get('Preco_Teto')}", f"{margem_b}%", 
                "> 6% Yield" if isinstance(margem_b, (int, float)) and margem_b > 0 else "< 6% Yield"
            ])
            
        # Lynch
        if lynch.get('Valor', 0) > 0:
            margem_l = lynch.get('Margem', 0)
            data_val.append([
                "Peter Lynch", "PEG Ratio", f"R$ {lynch.get('Valor')}", f"{margem_l}%", 
                "PEG < 1" if isinstance(margem_l, (int, float)) and margem_l > 0 else "PEG > 1"
            ])

        t_val = Table(data_val, colWidths=[4*cm, 3.5*cm, 3*cm, 2.5*cm, 3.5*cm])
        style_val = [
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1A237E")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('ALIGN', (2,0), (-1,-1), 'CENTER'),
            ('FONTSIZE', (0,0), (-1,-1), 9),
        ]
        
        for i in range(1, len(data_val)):
            upside_str = str(data_val[i][3]).replace('%', '')
            style_val.append(('TEXTCOLOR', (3, i), (3, i), get_color(upside_str)))

        t_val.setStyle(TableStyle(style_val))
        story.append(t_val)
        
        # Reverse DCF (Apenas se existir)
        if rev_dcf:
            story.append(Spacer(1, 0.3*cm))
            texto_reverse = f"<b>Reverse DCF:</b> Mercado precifica crescimento de <b>{rev_dcf.get('Implied_Growth', 0):.1%} a.a.</b>"
            story.append(Paragraph(texto_reverse, style_normal))

        story.append(Spacer(1, 0.5*cm))

        # --- 3. SENSIBILIDADE (Apenas se existir - Bancos não tem) ---
        sensib = valuation.get('Sensibilidade', {})
        if sensib:
            story.append(Paragraph("3. Matriz de Sensibilidade (DCF)", style_h1))
            matriz = sensib.get('Matriz', [])
            lbl_w = sensib.get('Labels_WACC', [])
            lbl_g = sensib.get('Labels_Growth', [])
            
            data_sens = [["Cresc. (g) \\ WACC"] + lbl_w]
            for i, row in enumerate(matriz):
                data_sens.append([lbl_g[i]] + [f"R$ {v:.2f}" for v in row])
                
            t_sens = Table(data_sens, colWidths=[3.5*cm, 3.5*cm, 3.5*cm, 3.5*cm])
            t_sens.setStyle(TableStyle([
                ('GRID', (0,0), (-1,-1), 1, colors.grey),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
                ('BACKGROUND', (0,0), (0,-1), colors.lightgrey),
                ('BACKGROUND', (2,2), (2,2), colors.yellow),
                ('FONTWEIGHT', (2,2), (2,2), 'BOLD'),
            ]))
            story.append(t_sens)
            story.append(Spacer(1, 0.5*cm))

        # --- 4. COMPARABLES ---
        if comparables:
            story.append(Paragraph("4. Análise Relativa (Pares)", style_h1))
            headers = ["Ind.", dados.get('ticker')] + [p['ticker'].replace('.SA','') for p in comparables['dados_pares']]
            
            def safe_fmt_comp(val, is_pct=False):
                if val is None: return "-"
                return f"{val:.1%}" if is_pct else f"{val:.2f}x"

            row_pl = ["P/L"] + [safe_fmt_comp(dados.get('pl'))] + [safe_fmt_comp(p.get('pl')) for p in comparables['dados_pares']]
            row_evebitda = ["EV/EBITDA"] + [safe_fmt_comp(dados.get('ev_ebitda'))] + [safe_fmt_comp(p.get('ev_ebitda')) for p in comparables['dados_pares']]
            
            t_comps = Table([headers, row_pl, row_evebitda])
            t_comps.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#00695C")),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('GRID', (0,0), (-1,-1), 1, colors.black),
                ('ALIGN', (1,0), (-1,-1), 'CENTER'),
            ]))
            story.append(t_comps)

        story.append(Spacer(1, 0.5*cm))

        # --- 5. TESE DE INVESTIMENTO ---
        story.append(Paragraph("5. Tese de Investimento (IA)", style_h1))
        
        if parecer_texto:
            paragraphs = parecer_texto.split('\n')
            for p in paragraphs:
                p = p.strip()
                if not p: continue
                
                # Tratamento básico de Markdown para ReportLab
                if p.startswith('###') or (p.startswith('**') and len(p) < 100):
                    clean_text = p.replace('#', '').replace('*', '').strip()
                    story.append(Paragraph(clean_text, style_h2))
                elif p.startswith('-'):
                    item_text = p[1:].strip()
                    item_text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', item_text)
                    story.append(Paragraph(f"• {item_text}", style_normal))
                else:
                    p_formatted = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', p)
                    story.append(Paragraph(p_formatted, style_normal))
                
                story.append(Spacer(1, 0.1*cm))

        doc.build(story)
        print(f"\n[PDF] Relatório V13 (Multi-Engine) Gerado: {nome_arquivo}")
        
    except Exception as e:
        print(f"\n[ERRO] Falha PDF: {e}")
        import traceback
        traceback.print_exc()