import streamlit as st
import pandas as pd
from collections import Counter
import numpy as np
from datetime import datetime, timedelta
import random

st.set_page_config(page_title="EuroMillions Predictor", layout="wide")

class EuroMillionsWeb:
    def __init__(self):
        self.data_path = "EuroMillions_2004-2025.xlsx"
        self.load_data()
        self.setup_ui()

    def load_data(self):
        try:
            data = pd.read_excel(self.data_path)
            data['Date'] = pd.to_datetime(data['Date']).dt.strftime('%Y-%m-%d')
            data['Numbers'] = data['Lucky Numbers'].apply(lambda x: [int(n) for n in x.split(',')])
            data['Stars'] = data['Lucky Stars'].apply(lambda x: [int(n) for n in x.split(',')])
            self.data = data.sort_values('Date', ascending=False)
            
            last_draw_date = self.data['Date'].max()
            two_years_ago = (pd.to_datetime(last_draw_date) - pd.DateOffset(years=2)).strftime('%Y-%m-%d')
            recent_data = self.data[self.data['Date'] >= two_years_ago]
            
            all_numbers = [num for sublist in self.data['Numbers'] for num in sublist]
            all_stars = [num for sublist in self.data['Stars'] for num in sublist]
            self.number_freq = Counter(all_numbers)
            self.star_freq = Counter(all_stars)
            
            recent_numbers = [num for sublist in recent_data['Numbers'] for num in sublist]
            recent_stars = [num for sublist in recent_data['Stars'] for num in sublist]
            self.recent_number_freq = Counter(recent_numbers)
            self.recent_star_freq = Counter(recent_stars)
            
            self.combined_number_freq = Counter()
            self.combined_star_freq = Counter()
            
            total_draws_historical = len(self.data)
            total_draws_recent = len(recent_data)
            
            for num in range(1, 51):
                historical_count = self.number_freq.get(num, 0)
                recent_count = self.recent_number_freq.get(num, 0)
                if total_draws_historical > 0 and total_draws_recent > 0:
                    historical_weight = (historical_count / total_draws_historical) * 0.3
                    recent_weight = (recent_count / total_draws_recent) * 0.7
                    self.combined_number_freq[num] = historical_weight + recent_weight
                else:
                    self.combined_number_freq[num] = 0
            
            for star in range(1, 13):
                historical_count = self.star_freq.get(star, 0)
                recent_count = self.recent_star_freq.get(star, 0)
                if total_draws_historical > 0 and total_draws_recent > 0:
                    historical_weight = (historical_count / total_draws_historical) * 0.3
                    recent_weight = (recent_count / total_draws_recent) * 0.7
                    self.combined_star_freq[star] = historical_weight + recent_weight
                else:
                    self.combined_star_freq[star] = 0
        except Exception as e:
            st.error(f"Erro ao carregar dados: {str(e)}")

    def generate_bets(self):
        bets = []
        numbers = list(range(1, 51))
        number_weights = [self.combined_number_freq[num] for num in numbers]
        number_prob = np.array(number_weights) / sum(number_weights) if sum(number_weights) > 0 else np.ones(len(numbers)) / len(numbers)

        stars = list(range(1, 13))
        star_weights = [self.combined_star_freq[star] for star in stars]
        star_prob = np.array(star_weights) / sum(star_weights) if sum(star_weights) > 0 else np.ones(len(stars)) / len(stars)

        for _ in range(5):
            selected_numbers = sorted(np.random.choice(numbers, size=5, replace=False, p=number_prob))
            selected_stars = sorted(np.random.choice(stars, size=2, replace=False, p=star_prob))
            bets.append((selected_numbers, selected_stars))
        return bets

    def setup_ui(self):
        st.title("EuroMillions Predictor")
        
        # Custom CSS for styling
        st.markdown("""
        <style>
        .number-ball {
            display: inline-block;
            background-color: #005baa;
            color: white;
            width: 40px;
            height: 40px;
            line-height: 40px;
            text-align: center;
            border-radius: 50%;
            margin: 5px;
            font-weight: bold;
        }
        .star-ball {
            display: inline-block;
            background-color: #ffd700;
            color: black;
            width: 40px;
            height: 40px;
            line-height: 40px;
            text-align: center;
            border-radius: 50%;
            margin: 5px;
            font-weight: bold;
        }
        .stButton>button {
            background-color: #005baa;
            color: white;
            border-radius: 5px;
            padding: 10px 20px;
            font-size: 16px;
        }
        </style>
        """, unsafe_allow_html=True)

        # Sidebar for controls
        st.sidebar.header("Controles")
        if st.sidebar.button("Gerar Apostas"):
            st.session_state.bets = self.generate_bets()
        
        if st.sidebar.button("Mostrar Estatísticas"):
            st.session_state.show_stats = True
        else:
            st.session_state.show_stats = False
        
        if st.sidebar.button("Adicionar Sorteio"):
            st.session_state.show_add_draw = True
        else:
            st.session_state.show_add_draw = False

        # Main content
        if 'bets' in st.session_state:
            st.subheader("Bilhete de Aposta")
            for i, (numbers, stars) in enumerate(st.session_state.bets, 1):
                st.write(f"**Aposta {i}**")
                cols = st.columns([4, 1])
                with cols[0]:
                    number_html = "".join(f'<span class="number-ball">{num:02d}</span>' for num in numbers)
                    st.markdown(number_html, unsafe_allow_html=True)
                with cols[1]:
                    star_html = "".join(f'<span class="star-ball">{star:02d}</span>' for star in stars)
                    st.markdown(star_html, unsafe_allow_html=True)
            st.markdown("**Preço Total: €12.50 (5 apostas x €2.50)**")

        # Last draws
        st.subheader("Últimos Sorteios")
        if not self.data.empty:
            last_two_draws = self.data.iloc[:2]
            for _, draw in last_two_draws.iterrows():
                st.write(f"**Data**: {draw['Date']}")
                number_html = "".join(f'<span class="number-ball">{num:02d}</span>' for num in draw['Numbers'])
                star_html = "".join(f'<span class="star-ball">{star:02d}</span>' for star in draw['Stars'])
                st.markdown(f"**Números**: {number_html}", unsafe_allow_html=True)
                st.markdown(f"**Estrelas**: {star_html}", unsafe_allow_html=True)
                st.write("")
        else:
            st.write("Nenhum sorteio disponível.")

        # Add draw form
        if st.session_state.get('show_add_draw', False):
            st.subheader("Adicionar Novo Sorteio")
            with st.form("add_draw_form"):
                date = st.text_input("Data (YYYY-MM-DD)")
                numbers = st.text_input("Números (5 números, 1-50, separados por vírgula)")
                stars = st.text_input("Estrelas (2 números, 1-12, separados por vírgula)")
                submit = st.form_submit_button("Guardar")
                if submit:
                    try:
                        numbers_list = [int(n.strip()) for n in numbers.split(',')]
                        stars_list = [int(n.strip()) for n in stars.split(',')]
                        if len(numbers_list) != 5 or len(stars_list) != 2:
                            raise ValueError("Precisa de 5 números e 2 estrelas")
                        new_row = pd.DataFrame({
                            'Date': [date],
                            'Lucky Numbers': [','.join(map(str, numbers_list))],
                            'Lucky Stars': [','.join(map(str, stars_list))]
                        })
                        self.data = pd.concat([new_row, self.data]).sort_values('Date', ascending=False)
                        self.data.to_excel(self.data_path, index=False)
                        self.load_data()
                        st.success("Sorteio adicionado com sucesso!")
                        st.session_state.show_add_draw = False
                    except Exception as e:
                        st.error(f"Dados inválidos: {str(e)}")

        # Statistics
        if st.session_state.get('show_stats', False):
            st.subheader("Estatísticas")
            st.write("**Números Mais Frequentes (com foco nos últimos 2 anos)**")
            cols = st.columns(5)
            for i, (num, score) in enumerate(self.combined_number_freq.most_common(10)):
                cols[i % 5].write(f"{num:02d}: {score:.3f} (score ponderado)")
            
            st.write("**Estrelas Mais Frequentes (com foco nos últimos 2 anos)**")
            cols = st.columns(5)
            for i, (star, score) in enumerate(self.combined_star_freq.most_common(5)):
                cols[i].write(f"{star:02d}: {score:.3f} (score ponderado)")
            
            st.write("*Nota: EuroMillions é um jogo de sorte. Nenhuma estratégia garante vitória.*")

if __name__ == "__main__":
    app = EuroMillionsWeb()