import streamlit as st
from typing import Dict, List, Optional
import os

# --- CONFIGURAÇÃO ---
st.set_page_config(
    page_title="Calculadora de Avaliação | b-Med",
    layout="centered",
    page_icon="🩺"
)

# --- CONSTANTES ---
BRAZIL_STATES = [
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", 
    "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"
]

# --- ESTRUTURA DE DADOS (GROUPS & NICHES) ---
GROUPS_DEFINITION = {
    "Ferramentas de Gestão e Fluxo": ["Prontuário Eletrônico", "Telemedicina", "Gestão de Consultório"],
    "Suporte à Diagnóstico e Conduta": ["Dispositivo Médico", "IA Diagnóstica", "Calculadoras Clínicas", "Monitoramento Remoto"],
    "Terapêuticas Digitais e Reabilitação": ["DTx", "Realidade Virtual", "Mudança de Hábito"]
}

ALL_NICHES = sorted([n for sublist in GROUPS_DEFINITION.values() for n in sublist])

def get_group_from_niche(niche: str) -> Optional[str]:
    for group, niches in GROUPS_DEFINITION.items():
        if niche in niches: return group
    return None

# --- STATE MANAGEMENT ---
def init_session_state():
    if "current_step" not in st.session_state: st.session_state.current_step = 1
    
    if "evaluation_data" not in st.session_state:
        st.session_state.evaluation_data = {
            "solution_name": "", 
            "evaluator_name": "", 
            "email": "",          
            "uf": "SP",           
            "crm_num": "",        
            "group": "",
            "niche": ""
        }
    
    if "scores" not in st.session_state: st.session_state.scores = {}

def navigate_to(step: int):
    st.session_state.current_step = step
    st.rerun()

# --- FUNÇÕES DE CÁLCULO COMPLEXAS ---

def calculate_sus_score(responses: List[int]) -> float:
    """Calcula o System Usability Scale (SUS). Retorna 0 a 100."""
    score = 0
    for i, val in enumerate(responses):
        if (i + 1) % 2 != 0: # Ímpar
            score += (val - 1)
        else: # Par
            score += (5 - val)
    return score * 2.5

def calculate_mars_score(sub_scores: Dict[str, float]) -> float:
    """Calcula média final do MARS."""
    values = list(sub_scores.values())
    if not values: return 0.0
    return sum(values) / len(values)

# --- INTERFACE DE USUÁRIO (UI) ---

def render_header():
    """Renderiza o Cabeçalho com o Logo da b-Med em todas as páginas."""
    logo_files = ["bmed slogan.jfif", "bmed_logo.png", "logo.jpg"]
    logo_loaded = False
    
    for logo_file in logo_files:
        if os.path.exists(logo_file):
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.image(logo_file, use_column_width=True)
            logo_loaded = True
            break
            
    if not logo_loaded:
        st.warning("⚠️ Imagem do logo não encontrada. Verifique o arquivo na pasta.")

    st.markdown("<h2 style='text-align: center;'>Calculadora de Avaliação</h2>", unsafe_allow_html=True)
    st.markdown("---")

# --- RENDERIZADORES DE GRUPOS ---

def render_group_1_management():
    tabs = st.tabs(["1.1 Interoperabilidade", "1.2 Segurança", "1.3 Usabilidade", "1.4 Estabilidade"])
    
    with tabs[0]:
        st.markdown("#### Interoperabilidade")
        score_1_1 = 0
        
        q1 = st.radio("Como o dado trafega entre sistemas?", 
            ["Não tem integração/CSV (0 pts)", "API Proprietária (5 pts)", "Padrão HL7 FHIR/v2 (10 pts)"], key="g1_q1")
        if "FHIR" in q1: score_1_1 += 10
        elif "API" in q1: score_1_1 += 5
        
        q2 = st.radio("O computador entende o que está escrito?", 
            ["Texto livre (0 pts)", "Vocabulários controlados (CID/TUSS/SNOMED) (10 pts)"], key="g1_q2")
        if "Vocabulários" in q2: score_1_1 += 10
        
        q3 = st.radio("Facilidade de conexão para desenvolvedores?",
            ["Pedir acesso ao suporte (0 pts)", "Documentação pública (Swagger/OpenAPI) (10 pts)"], key="g1_q3")
        if "Pública" in q3: score_1_1 += 10
        
        q4 = st.radio("Certificação SBIS-CFM?", ["Não (5 pts)", "Sim (10 pts)"], key="g1_q4")
        if "Sim" in q4: score_1_1 += 10
        else: score_1_1 += 5

        st.info(f"Pontuação Parcial: {score_1_1}/40")
        st.session_state.scores['1.1 Interoperabilidade'] = score_1_1

    with tabs[1]:
        st.markdown("#### Segurança e LGPD")
        score_1_2 = 0
        local = st.radio("Onde o dado é armazenado?", ["Nuvem/SaaS", "Dispositivo (Local)"], key="g1_sec_local")
        
        if local == "Nuvem/SaaS":
            st.radio("Servidor no Brasil ou com SCCs?", ["Sim", "Não"], key="g1_sec_cloud")
        else:
            st.radio("App garante Sandbox?", ["Sim", "Não"], key="g1_sec_sandbox")
        
        anon = st.radio("A IA treina com dados que identificam o paciente?", ["Sim (Risco Alto)", "Não (Liberado)"], key="g1_sec_anon")
        if anon == "Sim (Risco Alto)":
            st.error("🚨 **RISCO ÉTICO ALTO: NÃO USAR**")
            score_1_2 = 0
        else:
            score_1_2 = 10 
        st.session_state.scores['1.2 Segurança'] = score_1_2

    with tabs[2]:
        st.markdown("#### Usabilidade")
        score_1_3 = 0
        cliques = st.radio("Quantos cliques para prescrever Dipirona?", 
            ["Mais de 10 (0 pts)", "6 a 9 (5 pts)", "Menos de 5 (10 pts)"], key="g1_usa_clicks")
        if "Menos" in cliques: score_1_3 += 10
        elif "6 a 9" in cliques: score_1_3 += 5
        
        st.divider()
        st.caption("System Usability Scale (SUS)")
        sus_questions = [
            "1. Eu gostaria de usar este sistema frequentemente.",
            "2. Eu achei o sistema desnecessariamente complexo.",
            "3. Eu achei o sistema fácil de usar.",
            "4. Eu acho que precisaria de suporte técnico para usar.",
            "5. As funções do sistema estão muito bem integradas.",
            "6. Eu achei que o sistema tem muita inconsistência.",
            "7. A maioria das pessoas aprenderia muito rapidamente.",
            "8. Eu achei o sistema muito confuso/trabalhoso.",
            "9. Eu me senti muito confiante usando o sistema.",
            "10. Eu precisei aprender muitas coisas novas antes de usar."
        ]
        sus_responses = []
        with st.expander("Responder Questionário SUS"):
            for q in sus_questions:
                sus_responses.append(st.slider(q, 1, 5, 3, key=q))
        
        sus_final = calculate_sus_score(sus_responses)
        st.write(f"**Score SUS:** {sus_final}")
        
        if sus_final > 80: score_1_3 += 10
        elif sus_final >= 68: score_1_3 += 5
        elif sus_final >= 51: score_1_3 += 2
        
        st.session_state.scores['1.3 Usabilidade'] = score_1_3

    with tabs[3]:
        st.markdown("#### Estabilidade")
        score_1_4 = 0
        rpo = st.selectbox("RPO", ["> 7 horas (0 pts)", "3.5 horas/mês (5 pts)", "43 min/mês (10 pts)"], key="g1_rpo")
        if "43 min" in rpo: score_1_4 += 10
        elif "3.5 horas" in rpo: score_1_4 += 5
        
        rto = st.selectbox("RTO", ["Backup diário (0 pts)", "Tempo real/15min (10 pts)"], key="g1_rto")
        if "Tempo real" in rto: score_1_4 += 10
        
        failover = st.selectbox("Recuperação", ["Leva dias (0 pts)", "Redundância automática (10 pts)"], key="g1_fail")
        if "automática" in failover: score_1_4 += 10
        
        st.session_state.scores['1.4 Estabilidade'] = score_1_4

def render_group_2_diagnostic():
    tabs = st.tabs(["2.1 Científico", "2.2 Métricas", "2.3 Regulatório", "2.4 Segurança"])
    
    with tabs[0]:
        st.markdown("#### Validação Científica")
        validacao = st.radio("Tipo de Validação", [
            "Interna / Cruzada (0 pts)", "Separação Temporal (5 pts)", 
            "Externa: 1 Hospital (10 pts)", "Externa: >2 Hospitais (20 pts)"], key="g2_sci")
        
        val_points = 0
        if "20 pts" in validacao: val_points = 20
        elif "10 pts" in validacao: val_points = 10
        elif "5 pts" in validacao: val_points = 5
        st.session_state.scores['2.1 Científico'] = val_points

    with tabs[1]:
        st.markdown("#### Métricas")
        tipo_tool = st.selectbox("Tipo da ferramenta", ["Rastreio/Triagem", "Apoio ao Diagnóstico", "Monitorização"], key="g2_type")
        metric_score = 0
        
        if tipo_tool == "Rastreio/Triagem":
            if "≥" in st.radio("Sensibilidade", ["< 90% (0 pts)", "≥ 90% (10 pts)"], key="g2_sens"): metric_score += 10
            if "≥" in st.radio("VPN", ["< 95% (0 pts)", "≥ 95% (10 pts)"], key="g2_vpn"): metric_score += 10
        elif tipo_tool == "Apoio ao Diagnóstico":
            if "≥" in st.radio("Especificidade", ["< 85% (0 pts)", "≥ 85% (10 pts)"], key="g2_spec"): metric_score += 10
            if "≥" in st.radio("VPP", ["< 95% (0 pts)", "≥ 95% (10 pts)"], key="g2_vpp"): metric_score += 10
            if "≥" in st.radio("F1-Score", ["< 95% (0 pts)", "≥ 95% (10 pts)"], key="g2_f1"): metric_score += 10
        elif tipo_tool == "Monitorização":
            if "< 1" in st.radio("Falsos Alarmes", ["> 1/4h (0 pts)", "< 1/4h (10 pts)"], key="g2_alarm"): metric_score += 10
            if "4 horas" in st.radio("Lead Time", ["2 min (0 pts)", "4 horas (10 pts)"], key="g2_lead"): metric_score += 10
            if "≥ 20%" in st.radio("Precisão", ["< 20% (0 pts)", "≥ 20% (10 pts)"], key="g2_prec_mon"): metric_score += 10
            
        st.session_state.scores['2.2 Métricas'] = metric_score

    with tabs[2]:
        st.markdown("#### Regulatório")
        uso = st.radio("Uso Clínico?", ["Sim (SaMD)", "Não (Educacional)"], key="g2_reg_type")
        reg_score = 0
        
        if uso == "Sim (SaMD)":
            if st.radio("Registro ANVISA + Instruções PT-BR?", ["Sim", "Não"], key="g2_anvisa") == "Não":
                st.error("⛔ **BLOQUEIO ANVISA**")
            else:
                st.success("✅ Registro Validado")
                reg_score = 20
        else:
            if not st.checkbox("Disclaimer de Pesquisa?", key="g2_disc") or \
               st.radio("Conexão Prontuário", ["Dados Reais (Risco)", "Base Separada (20 pts)"], key="g2_con") == "Dados Reais (Risco)":
                st.error("🚨 Risco Ético")
            else:
                reg_score = 20
        st.session_state.scores['2.3 Regulatório'] = reg_score

    with tabs[3]:
        st.markdown("#### Segurança")
        if "Sim" in st.radio("Treino com dados identificados?", ["Sim (Risco)", "Não (Liberado)"], key="g2_sec"):
            st.error("🚨 **NÃO USAR**")
            st.session_state.scores['2.4 Segurança'] = 0
        else:
            st.session_state.scores['2.4 Segurança'] = 10

def render_group_3_dtx():
    tabs = st.tabs(["3.1 Evidência", "3.2 Engajamento (MARS)", "3.3 Conteúdo"])
    
    with tabs[0]:
        st.markdown("#### Evidência Clínica")
        evid = st.radio("Nível", ["Randomizado (20 pts)", "Pré-Pós (10 pts)", "Piloto (10 pts)"], key="g3_evid")
        st.session_state.scores['3.1 Evidência'] = 20 if "Randomizado" in evid else 10

    with tabs[1]:
        st.markdown("#### Engajamento (MARS)")
        c1, c2 = st.columns(2)
        with c1:
            st.write("**Engajamento**")
            me = sum([st.slider(l, 1, 5, 3, key=f"e{i}") for i, l in enumerate(["Diversão", "Interesse", "Customização", "Interatividade", "Alvo"])]) / 5
        with c2:
            st.write("**Funcionalidade**")
            mf = sum([st.slider(l, 1, 5, 3, key=f"f{i}") for i, l in enumerate(["Desempenho", "Facilidade", "Navegação", "Gestos"])]) / 4
        
        c3, c4 = st.columns(2)
        with c3:
            st.write("**Estética**")
            mes = sum([st.slider(l, 1, 5, 3, key=f"es{i}") for i, l in enumerate(["Layout", "Gráficos", "Apelo Visual"])]) / 3
        with c4:
            st.write("**Informação**")
            # --- CORREÇÃO AQUI: ITENS ESPECÍFICOS DO MARS 13-20 ---
            inf_labels = [
                "13. Seguro e Científico? (Crítico)",
                "14. Acurácia: Faz o que promete?",
                "15. Metas: Objetivos claros?",
                "16. Qualidade Texto: Acessível?",
                "17. Quantidade: Info suficiente?",
                "18. Evidência Visual: Gráficos claros?",
                "19. Credibilidade: Quem fez?",
                "20. Base Científica: Comprovada?"
            ]
            inf_scores = []
            for label in inf_labels:
                inf_scores.append(st.slider(label, 1, 5, 3, key=label))
                
            minf = sum(inf_scores) / 8
            
        mars_final = (me + mf + mes + minf) / 4
        st.write(f"**Nota MARS:** {mars_final:.2f}")
        
        pts = 20 if mars_final >= 4.0 else (10 if mars_final >= 3.0 else 0)
        st.session_state.scores['3.2 Engajamento'] = pts

    with tabs[2]:
        st.markdown("#### Conteúdo")
        pts = 10 if "habilitado" in st.radio("Autor:", ["Habilitado (10 pts)", "Não habilitado (0 pts)"], key="g3_cont") else 0
        st.session_state.scores['3.3 Conteúdo'] = pts

# --- RENDERIZADORES DAS TELAS (STEPS) ---

def render_step_1():
    """Tela de Login e Cadastro Inicial Atualizada"""
    st.subheader("Passo 1: Identificação")
    with st.form("id_form"):
        st.markdown("**Dados do Avaliador**")
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Nome Completo", value=st.session_state.evaluation_data["evaluator_name"])
            email = st.text_input("Email Corporativo", value=st.session_state.evaluation_data["email"])
        with col2:
            sub_col_1, sub_col_2 = st.columns([1, 2])
            with sub_col_1:
                uf_idx = BRAZIL_STATES.index(st.session_state.evaluation_data["uf"]) if st.session_state.evaluation_data["uf"] in BRAZIL_STATES else 24
                uf = st.selectbox("UF", BRAZIL_STATES, index=uf_idx)
            with sub_col_2:
                crm = st.text_input("Nº CRM / Matrícula", value=st.session_state.evaluation_data["crm_num"])
        
        st.markdown("---")
        st.markdown("**Dados da Solução**")
        solution = st.text_input("Nome da Solução / Software", value=st.session_state.evaluation_data["solution_name"])
        niche = st.selectbox("Selecione o Nicho:", ALL_NICHES)
        
        if st.form_submit_button("Iniciar Avaliação"):
            if niche and name and crm:
                st.session_state.evaluation_data.update({
                    "evaluator_name": name,
                    "email": email,
                    "uf": uf,
                    "crm_num": crm,
                    "solution_name": solution,
                    "group": get_group_from_niche(niche),
                    "niche": niche
                })
                navigate_to(2)
            else:
                st.error("Por favor, preencha Nome, CRM e Nicho da solução.")

def render_step_2():
    data = st.session_state.evaluation_data
    st.caption(f"Avaliador: **{data['evaluator_name']}** ({data['crm_num']}/{data['uf']}) | Solução: **{data['solution_name']}**")
    
    if data['group'] == "Ferramentas de Gestão e Fluxo":
        render_group_1_management()
    elif data['group'] == "Suporte à Diagnóstico e Conduta":
        render_group_2_diagnostic()
    elif data['group'] == "Terapêuticas Digitais e Reabilitação":
        render_group_3_dtx()
    
    st.divider()
    c1, c2 = st.columns([1, 2])
    if c1.button("<< Voltar"): navigate_to(1)
    if c2.button("Finalizar Relatório", type="primary"):
        st.balloons()
        st.subheader("📊 Resultado Consolidado")
        
        st.markdown(f"""
        **Avaliador:** {data['evaluator_name']}  
        **Email:** {data['email']}  
        **Registro:** {data['crm_num']}/{data['uf']}
        """)
        
        total = sum(st.session_state.scores.values())
        st.write(st.session_state.scores)
        st.metric("Nota Total", f"{total} pts")

def main():
    init_session_state()
    render_header()
    
    if st.session_state.current_step == 1: render_step_1()
    else: render_step_2()

if __name__ == "__main__":
    main()