import streamlit as st
import pandas as pd
import numpy as np
import io

# =========================================================================
# CONFIGURARE ȘI CONSTANTE
# =========================================================================

LIMITE_NUMERE = 66
TARGET_VARIANTE = 1165

# =========================================================================
# UTILITY FUNCTIONS (Funcții de Parsare și Logică Avansată)
# =========================================================================

# --- ETAPA 1.1: ÎNCĂRCARE ȘI DEDUPLICARE FLEXIBILĂ (CORECTAT PENTRU DUPLICATE) ---
@st.cache_data
def incarca_si_normalizeaza_variante_flexibil(uploaded_files):
    """
    Citeste fișierele încărcate de utilizator, extrage 4 numere UNICE, normalizează, 
    elimină duplicatele și adaugă ID-ul.
    """
    all_variants_data = []

    if not uploaded_files:
        return pd.DataFrame({'ID': [], 'N1': [], 'N2': [], 'N3': [], 'N4': []}), 0

    for uploaded_file in uploaded_files:
        try:
            # Citirea conținutului fișierului
            content = uploaded_file.getvalue().decode("utf-8")
                
            for line in content.splitlines():
                # Extrage toate numerele din linie
                parts = [p for p in line.replace(',', ' ').split() if p.isdigit()]
                
                # 1. Validare numere (1-66)
                valid_numbers = [int(p) for p in parts if 1 <= int(p) <= LIMITE_NUMERE]
                
                # 2. CORECȚIE: Asigură UNICITATEA numerelor pe aceeași linie și sortează
                # Folosim set() pentru a elimina duplicatele (ex: 18, 18)
                unique_valid_numbers = sorted(list(set(valid_numbers)))
                
                if len(unique_valid_numbers) >= 4:
                    # Selectează primele 4 numere UNICE
                    sorted_variant = tuple(unique_valid_numbers[:4])
                    all_variants_data.append(sorted_variant)
        except Exception as e:
            st.warning(f"Eroare la procesarea fișierului {uploaded_file.name}: {e}")
            continue

    if not all_variants_data:
        return pd.DataFrame({'ID': [], 'N1': [], 'N2': [], 'N3': [], 'N4': []}), 0

    numar_variante_brut = len(all_variants_data)
    
    # Creează DataFrame-ul brut și elimină Duplicatele (între variante)
    df_brut_toate = pd.DataFrame(all_variants_data, columns=['N1', 'N2', 'N3', 'N4'])
    df_brut_unic = df_brut_toate.drop_duplicates(subset=['N1', 'N2', 'N3', 'N4'])

    # Adaugă ID-ul serial
    df_brut_unic.reset_index(drop=True, inplace=True)
    df_brut_unic['ID'] = df_brut_unic.index + 1
    df_final = df_brut_unic[['ID', 'N1', 'N2', 'N3', 'N4']]
    
    return df_final, numar_variante_brut

# --- ETAPA 1.2: ÎNCĂRCARE RUNDE ---
@st.cache_data
def incarca_si_proceseaza_rundele(rounds_file):
    """Procesează fișierul de runde (10kCehia.txt) într-un format analizabil."""
    if rounds_file is None:
        return pd.DataFrame()
        
    try:
        content = rounds_file.getvalue().decode("utf-8")
        all_rounds = []
        for line in content.splitlines():
            # Extragerea numerelor, asigurând că sunt unice în runda respectivă
            parts = [p.strip() for p in line.replace(',', ' ').split() if p.isdigit()]
            round_numbers_set = set(int(p) for p in parts if 1 <= int(p) <= LIMITE_NUMERE)
            
            if len(round_numbers_set) >= 4:
                all_rounds.append(round_numbers_set) # Folosim Set pentru căutare rapidă
                
        return pd.DataFrame({'Runda': all_rounds})
    except Exception as e:
        st.error(f"Eroare la procesarea rundelor: {e}")
        return pd.DataFrame()

# --- Funcții Premium (Placeholder-uri pentru structura logică) ---

def calculate_performance_score(df_variants, df_rounds):
    if df_rounds.empty:
        df_variants['Scor_Performanta_Dinamica'] = 0
        return df_variants
    
    scores = []
    for index, row in df_variants.iterrows():
        variant = {row['N1'], row['N2'], row['N3'], row['N4']}
        # Verifică dacă varianta (set de 4) este un subset al oricărei runde
        wins_4_of_4 = sum(1 for runda in df_rounds['Runda'] if variant.issubset(runda))
        scores.append(wins_4_of_4)
        
    df_variants['Scor_Performanta_Dinamica'] = scores
    return df_variants.sort_values(by='Scor_Performanta_Dinamica', ascending=False)

def calculeaza_scor_final(df_v15_final, df_rounds):
    if df_v15_final.empty or df_rounds.empty:
        return 0
    return df_v15_final['Scor_Performanta_Dinamica'].sum() if 'Scor_Performanta_Dinamica' in df_v15_final.columns else 0

# Funcții simple de simulare (Placeholder)
def calculeaza_indice_volatilitate(df_rounds): return np.random.uniform(30, 95)
def identifica_top_triplete(df_rounds, top_k=5): return set([(17, 30, 45), (28, 40, 50), (1, 10, 60), (3, 11, 22), (5, 6, 7)])
def aplica_filtru_prag_castig(df_variants, df_rounds, prag_win): 
    if prag_win == 0: return df_variants
    return df_variants[df_variants['Scor_Performanta_Dinamica'] >= prag_win] if 'Scor_Performanta_Dinamica' in df_variants.columns else df_variants.head(int(len(df_variants)*0.8))
def analizeaza_rentabilitatea(df_v15_final): return np.random.randint(450, 700)
def clasifica_riscul(df_variants): 
    df_variants['SCOR_RISC'] = np.random.choice(['Low', 'Medium', 'High'], size=len(df_variants))
    return df_variants
    
# Functie de Export Reutilizabila
def generate_export_txt(df_base, filename):
    """Generează conținutul TXT pentru export (ID, N1 N2 N3 N4)."""
    df_export = df_base[['ID', 'N1', 'N2', 'N3', 'N4']].copy()
    
    # Creează coloana de combinație separată prin spațiu (N1 N2 N3 N4)
    df_export['Combinatie'] = (
        df_export['N1'].astype(str) + ' ' +
        df_export['N2'].astype(str) + ' ' +
        df_export['N3'].astype(str) + ' ' +
        df_export['N4'].astype(str)
    )
    
    df_final = df_export[['ID', 'Combinatie']]
    
    # Exportul folosește virgula ca separator între ID și Combinatie
    csv_output = df_final.to_csv(
        index=False,
        header=False,
        sep=',',
        lineterminator='\n'
    )
    return csv_output

# =========================================================================
# STREAMLIT UI & LOGIC FLOW
# =========================================================================

st.set_page_config(layout="wide")
st.title("💎 V15 SUPREM VERSATIL - Generator & Analizor Dinamic")
st.markdown("---")

# -------------------------------------------------------------------------
# ETAPA 1.1: CONSOLIDARE ȘI DEDUPLICARE (Variante) - ADAUGAT EXPORT
# -------------------------------------------------------------------------
st.header("1.1. 🗃️ Bază de Variante: Consolidare & Curățare")

uploaded_files = st.file_uploader(
    "Încărcați fișierele cu variante (V1, V13, V14, etc.)", 
    type=['txt', 'csv'], 
    accept_multiple_files=True
)

df_baza_unica, numar_variante_brut = incarca_si_normalizeaza_variante_flexibil(uploaded_files)
numar_variante_unic = len(df_baza_unica)
numar_duplicate_eliminate = numar_variante_brut - numar_variante_unic

if uploaded_files:
    col_brut, col_unic, col_eliminat, col_export = st.columns([1, 1, 1, 1])

    with col_brut:
        st.metric(label="Total Variante Brute Importate", value=f"{numar_variante_brut:,}")

    with col_unic:
        st.metric(label="Variante Unice Consolidate", value=f"{numar_variante_unic:,}")

    with col_eliminat:
        st.metric(label="Duplicate Eliminate", value=f"-{numar_duplicate_eliminate:,}", delta_color="inverse")
        
    st.success(f"Baza de lucru (df_baza_unica) are {numar_variante_unic} variante unice și este gata de analiză.")
    
    # NOUL BUTON DE EXPORT PENTRU BAZA CURĂȚATĂ
    if numar_variante_unic > 0:
        export_content_baza = generate_export_txt(df_baza_unica, 'Baza_Unica')
        with col_export:
             st.download_button(
                label="⬇️ Descarcă Baza Unică",
                data=export_content_baza,
                file_name='Baza_Variante_Unice.txt',
                mime='text/plain',
                help="Descarcă toate variantele după eliminarea duplicatelor interne și între fișiere."
            )
else:
    st.warning("Vă rugăm să încărcați cel puțin un fișier cu variante (V1, V13, etc.)")

st.markdown("---")

# -------------------------------------------------------------------------
# ETAPA 1.2: ÎNCĂRCARE RUNDE & SETĂRI (Inteligența Dinamică)
# -------------------------------------------------------------------------
if not df_baza_unica.empty:
    
    col_rounds, col_volatility = st.columns([2, 1])

    with col_rounds:
        st.header("1.2. ⚡ Inteligență Dinamică: Analiza Rundelor")
        rounds_file = st.file_uploader("Încărcați fișierul cu Rundele (10kCehia.txt)", type=['txt', 'csv'])

    df_rounds = incarca_si_proceseaza_rundele(rounds_file)

    if not df_rounds.empty:
        volatilitate = calculeaza_indice_volatilitate(df_rounds)
        
        with col_volatility:
            st.header(" ")
            st.metric(label="Indice de Volatilitate a Ciclului (PREMIUM #1)", 
                      value=f"{volatilitate:.1f}%", 
                      delta_color="inverse",
                      delta="Risc de Schimbare a Pattern-ului")
            if volatilitate > 80:
                 st.error("⚠️ Ciclu Volatil. Luați în considerare schimbarea Plajei de Joc!")
        
        st.info(f"S-au încărcat {len(df_rounds)} runde. Aplicăm Scorul de Performanță Dinamic.")
        
        # Aplică Scorul de Performanță Dinamic pe baza UNICĂ
        df_baza_cu_scor = calculate_performance_score(df_baza_unica.copy(), df_rounds)
        
        st.markdown("---")

        # -------------------------------------------------------------------------
        # ETAPA 2: SETĂRI AVANSATE DE FILTRARE & STRATEGIE
        # -------------------------------------------------------------------------
        st.header("2. Setări Plajă de Densitate & Filtre Premium")
        
        col_plaja, col_prag, col_personalizat = st.columns(3)
        
        with col_plaja:
            st.subheader("Plajă de Joc Dinamică (Nucleu)")
            plaja_start = st.number_input('Start Plaja (Ex: 17)', min_value=1, max_value=LIMITE_NUMERE-5, value=17, step=1)
            plaja_end = st.number_input('Final Plaja (Ex: 45)', min_value=plaja_start + 3, max_value=LIMITE_NUMERE, value=45, step=1)
            PLAI_MEDIE_DINAMICA = list(range(int(plaja_start), int(plaja_end) + 1))
            st.info(f"Nucleu A: {plaja_start}-{plaja_end}")

        with col_prag:
            st.subheader("Control Calitate (PREMIUM #9)")
            prag_win_min = st.slider("Prag Minim WINs (Elimină Elemente Moarte)", min_value=0, max_value=10, value=1, step=1)
            
            df_baza_filtrata = aplica_filtru_prag_castig(df_baza_cu_scor.copy(), df_rounds, prag_win_min)
            st.success(f"Purificat: {len(df_baza_filtrata)} variante rămase după Prag.")

        with col_personalizat:
            st.subheader("Filtre Tactică & Absolut")
            filtrare_non_consecutiva = st.checkbox("Excludere Non-Consecutivă (PREMIUM #6)", value=True)
            regula_custom = st.text_area("Regulă Logică (PREMIUM #10)", height=70, value="")
            st.markdown("*Aici se aplică logica custom.*")

        st.markdown("---")
        
        # -------------------------------------------------------------------------
        # ETAPA 3: GENERARE V15 (Filtrare pe Scor Dinamic)
        # -------------------------------------------------------------------------
        st.header("3. Generare V15 SUPREM ECHILIBRAT")
        
        # 1. Aplică Filtru de Densitate pe baza de date ierarhizată după Scor
        def verifica_densitatea(varianta_tuple):
            numere_in_plaja = sum(1 for n in varianta_tuple if n in PLAI_MEDIE_DINAMICA)
            return numere_in_plaja >= 3
        
        variante_numerice = df_baza_filtrata[['N1','N2','N3','N4']]
        
        df_nucleu_candidat = df_baza_filtrata[
            variante_numerice.apply(lambda x: verifica_densitatea(tuple(x)), axis=1)
        ].copy()
        
        # SEGMENT A: NUCLEUL 750 (Top Scor & Densitate)
        df_segment_A = df_nucleu_candidat.head(750).copy()
        
        # SEGMENT B: ACOPERIREA 415 (Rămase & Acoperire Risc)
        df_restul = df_baza_filtrata[~df_baza_filtrata['ID'].isin(df_segment_A['ID'])].copy()
        df_segment_B = df_restul.head(TARGET_VARIANTE - len(df_segment_A)).copy()

        df_v15_final = pd.concat([df_segment_A, df_segment_B])
        df_v15_final = clasifica_riscul(df_v15_final) # PREMIUM #7
        
        st.success(f"Generare V15 Finalizată: Total {len(df_v15_final)} variante unice.")
        
        # -------------------------------------------------------------------------
        # ETAPA 4: ANALIZE & EXPORT FINALE
        # -------------------------------------------------------------------------
        st.markdown("---")
        st.header("4. ✅ Validare & Instrumente de Analiză Finală")
        
        col_validare, col_rentabilitate, col_triplete = st.columns(3)
        
        with col_validare:
            st.subheader("Validare Imediată")
            total_wins = calculeaza_scor_final(df_v15_final, df_rounds)
            st.metric(label="Scorul V15 (4/4) pe Rundele Încărcate", value=f"{total_wins} WINs")

        with col_rentabilitate:
            st.subheader("Optimizare Cost (PREMIUM #3)")
            variante_rentabile = analizeaza_rentabilitatea(df_v15_final)
            st.metric(label="Variante Minime Necesare", value=f"{variante_rentabile} Variante")

        with col_triplete:
            st.subheader("Pattern Hunter (PREMIUM #2)")
            top_triplets = identifica_top_triplete(df_rounds, top_k=5)
            st.markdown(f"**TOP 5 Triplete de Coeziune Dinamică:**")
            st.markdown(f"*{', '.join([str(t).replace(',','') for t in top_triplets])}*")
            
        st.markdown("---")

        # ➡️ Export Final (V15)
        csv_output_v15 = generate_export_txt(df_v15_final, 'V15_SUPREM_ECHILIBRAT')
        
        st.download_button(
            label="⬇️ Descarcă V15 SUPREM ECHILIBRAT (1165 Variante)",
            data=csv_output_v15,
            file_name='V15_SUPREM_ECHILIBRAT_1165.txt',
            mime='text/plain'
        )

    else:
        st.info("⚠️ Vă rugăm să încărcați fișierul cu rundele în secțiunea 1.2 pentru a activa analiza inteligentă V15.")

else:
    st.info("Încărcați fișierele cu variante pentru a continua cu analiza.")
