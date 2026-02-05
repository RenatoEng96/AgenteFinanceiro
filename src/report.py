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

        # --- ESTILOS ---
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
        story.append(Paragraph(f"<b>Perfil Estratégico:</b> {perfil_empresa}", style_destaque_box))
        story.append(Spacer(1, 0.5*cm))

        # --- 1. DASHBOARD ---
        story.append(Paragraph("1. Dashboard de Fundamentos", style_h1))
        
        def fmt(val, sulfixo="", multiplicador=1):
            if val is None or val == "": return "-"
            try: return f"{float(val)*multiplicador:.2f}{sulfixo}"
            except: return str(val)

        data_fund = [
            ["Cotação", f"R$ {fmt(dados.get('cotacao'), '', 1)}", "P/L", fmt(dados.get('pl'), "x")],
            ["Div. Yield", fmt(dados.get('dy_anual'), "%", 100), "P/VP", fmt(dados.get('pvp'), "x")],
            ["ROE", fmt(dados.get('roe'), "%", 100), "EV/EBITDA", fmt(dados.get('ev_ebitda'), "x")],
            ["Margem Líq.", fmt(dados.get('margem_liq'), "%", 100), "LPA", f"R$ {fmt(dados.get('lpa_yahoo'))}"]
        ]
        
        t_fund = Table(data_fund, colWidths=[3.5*cm, 4.5*cm, 3.5*cm, 4.5*cm])
        t_fund.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('BACKGROUND', (0,0), (0,-1), colors.HexColor("#F5F5F5")),
            ('BACKGROUND', (2,0), (2,-1), colors.HexColor("#F5F5F5")),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ]))
        story.append(t_fund)
        if 'moat_score' in dados:
            story.append(Spacer(1, 0.2*cm))
            story.append(Paragraph(f"<b>Economic Moat Score:</b> {dados.get('moat_score')}/10 - {dados.get('moat_justificativa')}", style_normal))

        # --- 2. VALUATION INTRÍNSECO ---
        story.append(Paragraph("2. Modelagem de Valor Intrínseco (Absoluto)", style_h1))
        
        dcf = valuation.get('DCF_Adaptativo', {}) or {}
        graham = valuation.get('Graham', {}) or {}
        bazin = valuation.get('Bazin', {}) or {}
        lynch = valuation.get('Peter_Lynch', {}) or {}
        
        data_val = [["Modelo", "Foco", "Preço Justo", "Upside", "Status"]]
        
        for model_name, model_data in [("DCF / DDM", dcf), ("Graham", graham), ("Bazin", bazin), ("Peter Lynch", lynch)]:
             if model_data:
                valor = model_data.get('Valor') or model_data.get('Preco_Teto')
                margem = model_data.get('Margem')
                status = "Aguardando"
                if isinstance(margem, (int, float)):
                    status = "Descontado" if margem > 0 else "Caro"
                    margem = f"{margem}%"
                
                if valor and valor > 0:
                    data_val.append([model_name, "Intrínseco", f"R$ {valor}", margem, status])

        t_val = Table(data_val, colWidths=[4*cm, 3.5*cm, 3.5*cm, 2.5*cm, 3.5*cm])
        t_val.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1A237E")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('ALIGN', (2,0), (-1,-1), 'CENTER'),
        ]))
        story.append(t_val)
        
        # --- 3. ANÁLISE RELATIVA (A GRANDE MUDANÇA) ---
        if comparables:
            story.append(Paragraph("3. Valuation Relativo & Pares", style_h1))
            
            # Tabela de Comparação Direta
            pares = comparables['dados_pares']
            headers = ["Ticker", "P/L", "EV/EBITDA", "P/VP", "ROE"]
            
            def safe(d, k, is_pct=False):
                v = d.get(k)
                if v is None: return "-"
                return f"{v:.1%}" if is_pct else f"{v:.2f}x"
                
            data_comps = [headers]
            # Adiciona o Alvo
            data_comps.append([
                f"{dados.get('ticker')} (Alvo)", 
                safe(dados, 'pl'), safe(dados, 'ev_ebitda'), safe(dados, 'pvp'), safe(dados, 'roe', True)
            ])
            # Adiciona a Média
            medias = comparables['medias_setor']
            data_comps.append([
                "MÉDIA DO SETOR",
                safe(medias, 'pl'), safe(medias, 'ev_ebitda'), safe(medias, 'pvp'), safe(medias, 'roe', True)
            ])
            # Adiciona Pares Individuais
            for p in pares:
                data_comps.append([
                    p['ticker'].replace('.SA',''),
                    safe(p, 'pl'), safe(p, 'ev_ebitda'), safe(p, 'pvp'), safe(p, 'roe', True)
                ])
            
            t_comps = Table(data_comps, colWidths=[3.5*cm, 3*cm, 3.5*cm, 3*cm, 3*cm])
            t_comps.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#00695C")), # Cabeçalho Verde
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('BACKGROUND', (1,0), (1,-1), colors.HexColor("#E0F2F1")), # Destaque Alvo
                ('BACKGROUND', (2,0), (2,-1), colors.HexColor("#FFEBEE")), # Destaque Média
                ('GRID', (0,0), (-1,-1), 1, colors.black),
                ('ALIGN', (1,0), (-1,-1), 'CENTER'),
                ('FONTWEIGHT', (0,1), (-1,1), 'BOLD'), # Negrito no Alvo
                ('FONTWEIGHT', (0,2), (-1,2), 'BOLD'), # Negrito na Média
            ]))
            story.append(t_comps)
            story.append(Spacer(1, 0.4*cm))
            
            # Tabela de Preços Implícitos (NOVO)
            precos = comparables.get('precos_implicitos', {})
            story.append(Paragraph("<b>Preço Implícito por Múltiplos (Se negociasse na média):</b>", style_normal))
            
            data_impl = [["Métrica", "Preço Implícito", "Upside/Downside vs Tela"]]
            cotacao = dados.get('cotacao', 0)
            
            for k, v in precos.items():
                nome_metrica = k.replace('Target_', 'Múltiplo ')
                upside = ((v - cotacao) / cotacao) * 100 if cotacao > 0 else 0
                cor = colors.green if upside > 0 else colors.red
                data_impl.append([nome_metrica, f"R$ {v:.2f}", f"{upside:.1f}%"])
                
            t_impl = Table(data_impl, colWidths=[5*cm, 5*cm, 5*cm])
            t_impl.setStyle(TableStyle([
                 ('GRID', (0,0), (-1,-1), 1, colors.grey),
                 ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
                 ('ALIGN', (1,0), (-1,-1), 'CENTER'),
            ]))
            story.append(t_impl)

        # --- 4. TESE DE INVESTIMENTO ---
        story.append(Spacer(1, 0.5*cm))
        story.append(Paragraph("4. Tese de Investimento (IA Analítica)", style_h1))
        
        if parecer_texto:
            # Renderização de Markdown básico
            linhas = parecer_texto.split('\n')
            for linha in linhas:
                linha = linha.strip()
                if not linha: continue
                if linha.startswith('##'):
                    story.append(Paragraph(linha.replace('#','').strip(), style_h2))
                elif linha.startswith('-'):
                    story.append(Paragraph(f"• {linha[1:].strip()}", style_normal))
                else:
                    # Negrito simples
                    linha = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', linha)
                    story.append(Paragraph(linha, style_normal))
                story.append(Spacer(1, 0.1*cm))

        doc.build(story)
        print(f"\n[PDF] Relatório V12 (Completo) Gerado: {nome_arquivo}")
        
    except Exception as e:
        print(f"\n[ERRO] Falha PDF: {e}")
        import traceback
        traceback.print_exc()