import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine, text
import json
from datetime import datetime, timedelta
import io

# Configure Streamlit page
st.set_page_config(
    page_title="Premier League Football Analysis",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .title-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin: 20px 0;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# DATABASE CONNECTION
# ============================================================================

@st.cache_resource
def get_database_engine():
    """Create and cache database connection"""
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        db_url = f"postgresql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"
        engine = create_engine(db_url)
        return engine
    except Exception as e:
        st.error(f"❌ Database connection failed: {e}")
        return None

# ============================================================================
# DATA RETRIEVAL FUNCTIONS
# ============================================================================

def execute_query(engine, query):
    """Execute SQL query and return DataFrame"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text(query))
            df = pd.DataFrame(result.fetchall(), columns=result.keys())
            return df
    except Exception as e:
        st.error(f"Query execution error: {e}")
        return pd.DataFrame()

def get_teams_stats(engine):
    """Get statistics for all teams"""
    query = """
    SELECT 
        e.nom_equipe,
        COUNT(DISTINCT m.id_match) as total_matches,
        COUNT(DISTINCT j.id_joueur) as total_players,
        ROUND(AVG(CAST(rm.buts_marques AS FLOAT)), 2) as avg_goals_for,
        ROUND(AVG(CAST(rm.buts_contre AS FLOAT)), 2) as avg_goals_against
    FROM equipe e
    LEFT JOIN match m ON e.id_equipe = m.equipe_domicile_id OR e.id_equipe = m.equipe_exterieur_id
    LEFT JOIN joueur j ON e.id_equipe = j.equipe_id
    LEFT JOIN resultatmatch rm ON e.id_equipe = rm.equipe_id AND m.id_match = rm.match_id
    GROUP BY e.nom_equipe
    ORDER BY total_matches DESC
    """
    return execute_query(engine, query)

def get_top_scorers(engine, limit=10):
    """Get top scoring players"""
    query = f"""
    SELECT 
        j.nom_joueur,
        e.nom_equipe,
        SUM(CAST(sj.buts AS INTEGER)) as total_goals,
        SUM(CAST(sj.passes_decisives AS INTEGER)) as assists,
        COUNT(DISTINCT sj.id_statistique_joueur) as appearances
    FROM joueur j
    JOIN equipe e ON j.equipe_id = e.id_equipe
    LEFT JOIN statistiquejoueur sj ON j.id_joueur = sj.joueur_id
    WHERE sj.buts IS NOT NULL AND sj.buts != ''
    GROUP BY j.nom_joueur, e.nom_equipe
    ORDER BY total_goals DESC
    LIMIT {limit}
    """
    return execute_query(engine, query)

def get_match_data(engine, team_name=None):
    """Get all matches or filter by team"""
    query = """
    SELECT 
        m.date_match,
        e1.nom_equipe as domicile,
        e2.nom_equipe as exterieur,
        COALESCE(rm.buts_marques, 0) as buts_domicile,
        COALESCE(rm.buts_contre, 0) as buts_exterieur,
        CASE 
            WHEN CAST(rm.buts_marques AS INTEGER) > CAST(rm.buts_contre AS INTEGER) THEN 'Win'
            WHEN CAST(rm.buts_marques AS INTEGER) = CAST(rm.buts_contre AS INTEGER) THEN 'Draw'
            ELSE 'Loss'
        END as result
    FROM match m
    JOIN equipe e1 ON m.equipe_domicile_id = e1.id_equipe
    JOIN equipe e2 ON m.equipe_exterieur_id = e2.id_equipe
    LEFT JOIN resultatmatch rm ON m.id_match = rm.match_id
    ORDER BY m.date_match DESC
    """
    
    if team_name:
        query = query.replace(
            "ORDER BY m.date_match DESC",
            f"WHERE e1.nom_equipe = '{team_name}' OR e2.nom_equipe = '{team_name}'\nORDER BY m.date_match DESC"
        )
    
    return execute_query(engine, query)

def get_player_stats(engine, team_name=None):
    """Get detailed player statistics"""
    query = """
    SELECT 
        j.nom_joueur,
        e.nom_equipe,
        j.poste_principal,
        j.nationalite,
        COUNT(DISTINCT sj.id_statistique_joueur) as appearances,
        COALESCE(SUM(CAST(sj.buts AS INTEGER)), 0) as total_goals,
        COALESCE(SUM(CAST(sj.passes_decisives AS INTEGER)), 0) as total_assists,
        ROUND(AVG(CAST(sj.note AS FLOAT)), 2) as avg_rating,
        COALESCE(SUM(CAST(sj.passes_reussies AS INTEGER)), 0) as total_passes
    FROM joueur j
    JOIN equipe e ON j.equipe_id = e.id_equipe
    LEFT JOIN statistiquejoueur sj ON j.id_joueur = sj.joueur_id
    GROUP BY j.nom_joueur, e.nom_equipe, j.poste_principal, j.nationalite
    ORDER BY total_goals DESC
    """
    
    if team_name:
        query = query.replace(
            "GROUP BY j.nom_joueur",
            f"WHERE e.nom_equipe = '{team_name}'\nGROUP BY j.nom_joueur"
        )
    
    return execute_query(engine, query)

def get_team_performance(engine, team_name):
    """Get performance metrics for a specific team"""
    query = f"""
    SELECT 
        e.nom_equipe,
        COUNT(DISTINCT m.id_match) as total_matches,
        SUM(CASE 
            WHEN CAST(rm.buts_marques AS INTEGER) > CAST(rm.buts_contre AS INTEGER) THEN 1 
            ELSE 0 
        END) as wins,
        SUM(CASE 
            WHEN CAST(rm.buts_marques AS INTEGER) = CAST(rm.buts_contre AS INTEGER) THEN 1 
            ELSE 0 
        END) as draws,
        SUM(CASE 
            WHEN CAST(rm.buts_marques AS INTEGER) < CAST(rm.buts_contre AS INTEGER) THEN 1 
            ELSE 0 
        END) as losses,
        SUM(CAST(rm.buts_marques AS INTEGER)) as goals_for,
        SUM(CAST(rm.buts_contre AS INTEGER)) as goals_against
    FROM equipe e
    LEFT JOIN match m ON e.id_equipe = m.equipe_domicile_id
    LEFT JOIN resultatmatch rm ON m.id_match = rm.match_id AND rm.equipe_id = e.id_equipe
    WHERE e.nom_equipe = '{team_name}'
    GROUP BY e.nom_equipe
    """
    return execute_query(engine, query)

def get_all_teams(engine):
    """Get list of all teams"""
    query = "SELECT DISTINCT nom_equipe FROM equipe ORDER BY nom_equipe"
    df = execute_query(engine, query)
    return df['nom_equipe'].tolist() if not df.empty else []

# ============================================================================
# VISUALIZATION FUNCTIONS
# ============================================================================

def create_goals_chart(df):
    """Create bar chart for goals"""
    fig = px.bar(
        df,
        x='domicile',
        y='buts_domicile',
        title='Goals Scored by Home Teams',
        labels={'buts_domicile': 'Goals', 'domicile': 'Team'},
        color='buts_domicile',
        color_continuous_scale='Viridis'
    )
    fig.update_layout(height=400, hovermode='x unified')
    return fig

def create_team_stats_chart(df):
    """Create radar chart for team statistics"""
    if df.empty:
        st.warning("No data available for visualization")
        return None
    
    fig = px.bar(
        df.head(10),
        x='nom_equipe',
        y=['avg_goals_for', 'avg_goals_against'],
        title='Top 10 Teams: Goals For vs Against',
        labels={'value': 'Average Goals', 'nom_equipe': 'Team'},
        barmode='group'
    )
    fig.update_layout(height=400, hovermode='x unified')
    return fig

def create_scorers_chart(df):
    """Create horizontal bar chart for top scorers"""
    if df.empty:
        st.warning("No data available")
        return None
    
    fig = px.barh(
        df,
        x='total_goals',
        y='nom_joueur',
        color='total_goals',
        color_continuous_scale='Reds',
        title='Top Scorers in Premier League',
        labels={'total_goals': 'Goals', 'nom_joueur': 'Player'}
    )
    fig.update_layout(height=500, hovermode='closest')
    return fig

def create_performance_gauge(wins, draws, losses):
    """Create gauge chart for team performance"""
    win_rate = wins / (wins + draws + losses) if (wins + draws + losses) > 0 else 0
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=win_rate * 100,
        title={'text': "Win Rate (%)"},
        delta={'reference': 50},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 33], 'color': "#ff6b6b"},
                {'range': [33, 66], 'color': "#ffd93d"},
                {'range': [66, 100], 'color': "#6bcf7f"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 50
            }
        }
    ))
    fig.update_layout(height=400)
    return fig

def create_result_distribution(df):
    """Create pie chart for result distribution"""
    if df.empty:
        st.warning("No data available")
        return None
    
    result_counts = df['result'].value_counts()
    colors = {'Win': '#6bcf7f', 'Draw': '#ffd93d', 'Loss': '#ff6b6b'}
    
    fig = px.pie(
        values=result_counts.values,
        names=result_counts.index,
        title='Match Results Distribution',
        color_discrete_map=colors
    )
    fig.update_layout(height=400)
    return fig

# ============================================================================
# MAIN APP
# ============================================================================

def main():
    # Header
    st.markdown("""
        <div class="title-section">
            <h1>⚽ Premier League Football Analysis Dashboard</h1>
            <p>Interactive data visualization and analysis of 2024-2025 season</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Initialize database connection
    engine = get_database_engine()
    if engine is None:
        st.stop()
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters & Navigation")
    
    page = st.sidebar.radio(
        "Select View",
        ["📊 Dashboard", "⚽ Teams", "👥 Players", "🎯 Matches", "📈 Detailed Analysis"]
    )
    
    # Get teams for filtering
    all_teams = get_all_teams(engine)
    
    # ========================================================================
    # PAGE: DASHBOARD
    # ========================================================================
    if page == "📊 Dashboard":
        st.header("Overall League Statistics")
        
        # Get overall stats
        teams_stats = get_teams_stats(engine)
        top_scorers = get_top_scorers(engine, limit=10)
        
        if not teams_stats.empty:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Teams", len(teams_stats))
            with col2:
                st.metric("Total Players", int(teams_stats['total_players'].sum()))
            with col3:
                st.metric("Total Matches", int(teams_stats['total_matches'].sum()))
            with col4:
                avg_goals = teams_stats['avg_goals_for'].mean()
                st.metric("Avg Goals/Match", f"{avg_goals:.2f}")
            
            # Charts
            col1, col2 = st.columns(2)
            
            with col1:
                st.plotly_chart(create_team_stats_chart(teams_stats), use_container_width=True)
            
            with col2:
                st.plotly_chart(create_scorers_chart(top_scorers), use_container_width=True)
            
            # Top scorers table
            st.subheader("🏆 Top Scorers")
            st.dataframe(top_scorers, use_container_width=True, hide_index=True)
    
    # ========================================================================
    # PAGE: TEAMS
    # ========================================================================
    elif page == "⚽ Teams":
        st.header("Team Analysis")
        
        selected_team = st.sidebar.selectbox("Select Team", all_teams)
        
        if selected_team:
            team_perf = get_team_performance(engine, selected_team)
            team_matches = get_match_data(engine, selected_team)
            team_players = get_player_stats(engine, selected_team)
            
            if not team_perf.empty:
                perf_row = team_perf.iloc[0]
                
                # Performance metrics
                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    st.metric("Matches", int(perf_row['total_matches']))
                with col2:
                    st.metric("Wins", int(perf_row['wins']))
                with col3:
                    st.metric("Draws", int(perf_row['draws']))
                with col4:
                    st.metric("Losses", int(perf_row['losses']))
                with col5:
                    goal_diff = int(perf_row['goals_for']) - int(perf_row['goals_against'])
                    st.metric("Goal Diff", goal_diff)
                
                # Performance gauge
                wins = int(perf_row['wins'])
                draws = int(perf_row['draws'])
                losses = int(perf_row['losses'])
                
                col1, col2 = st.columns(2)
                with col1:
                    st.plotly_chart(create_performance_gauge(wins, draws, losses), use_container_width=True)
                
                with col2:
                    if not team_matches.empty:
                        st.plotly_chart(create_result_distribution(team_matches), use_container_width=True)
            
            # Recent matches
            st.subheader("Recent Matches")
            if not team_matches.empty:
                st.dataframe(team_matches, use_container_width=True, hide_index=True)
            
            # Team players
            st.subheader("Team Squad")
            if not team_players.empty:
                st.dataframe(team_players, use_container_width=True, hide_index=True)
    
    # ========================================================================
    # PAGE: PLAYERS
    # ========================================================================
    elif page == "👥 Players":
        st.header("Player Statistics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            selected_team = st.selectbox("Filter by Team (optional)", ["All Teams"] + all_teams)
        
        team_filter = None if selected_team == "All Teams" else selected_team
        
        # Get player stats
        if selected_team == "All Teams":
            top_scorers = get_top_scorers(engine, limit=20)
            st.subheader("Top 20 Scorers Across All Teams")
        else:
            top_scorers = get_player_stats(engine, team_filter)
            st.subheader(f"All Players - {team_filter}")
        
        if not top_scorers.empty:
            st.dataframe(top_scorers, use_container_width=True, hide_index=True)
            
            # Download CSV
            csv = top_scorers.to_csv(index=False)
            st.download_button(
                label="📥 Download Player Stats as CSV",
                data=csv,
                file_name=f"player_stats_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    # ========================================================================
    # PAGE: MATCHES
    # ========================================================================
    elif page == "🎯 Matches":
        st.header("Match Results")
        
        match_data = get_match_data(engine)
        
        if not match_data.empty:
            # Summary statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                total_matches = len(match_data)
                st.metric("Total Matches", total_matches)
            with col2:
                total_goals = match_data['buts_domicile'].sum() + match_data['buts_exterieur'].sum()
                st.metric("Total Goals", int(total_goals))
            with col3:
                avg_goals = total_goals / total_matches if total_matches > 0 else 0
                st.metric("Avg Goals/Match", f"{avg_goals:.2f}")
            
            # Visualizations
            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(create_goals_chart(match_data.head(15)), use_container_width=True)
            with col2:
                st.plotly_chart(create_result_distribution(match_data), use_container_width=True)
            
            # All matches table
            st.subheader("All Matches")
            st.dataframe(match_data, use_container_width=True, hide_index=True)
            
            # Download CSV
            csv = match_data.to_csv(index=False)
            st.download_button(
                label="📥 Download Match Data as CSV",
                data=csv,
                file_name=f"match_data_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    # ========================================================================
    # PAGE: DETAILED ANALYSIS
    # ========================================================================
    elif page == "📈 Detailed Analysis":
        st.header("Advanced Analytics")
        
        analysis_type = st.radio(
            "Select Analysis Type",
            ["League Overview", "Team Comparison", "Player Comparison", "Goal Trends"]
        )
        
        if analysis_type == "League Overview":
            st.subheader("League-Wide Statistics")
            teams_stats = get_teams_stats(engine)
            if not teams_stats.empty:
                st.dataframe(teams_stats, use_container_width=True, hide_index=True)
                
                # Summary statistics
                st.subheader("League Summary")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**Most Matches:** {teams_stats.loc[teams_stats['total_matches'].idxmax(), 'nom_equipe']} ({int(teams_stats['total_matches'].max())} matches)")
                with col2:
                    st.write(f"**Highest Scoring:** {teams_stats.loc[teams_stats['avg_goals_for'].idxmax(), 'nom_equipe']} ({teams_stats['avg_goals_for'].max():.2f} goals/match)")
                with col3:
                    st.write(f"**Best Defense:** {teams_stats.loc[teams_stats['avg_goals_against'].idxmin(), 'nom_equipe']} ({teams_stats['avg_goals_against'].min():.2f} goals conceded/match)")
        
        elif analysis_type == "Team Comparison":
            st.subheader("Compare Teams")
            teams_to_compare = st.multiselect("Select Teams to Compare", all_teams, default=all_teams[:3])
            
            if teams_to_compare:
                comparison_data = []
                for team in teams_to_compare:
                    team_data = get_team_performance(engine, team)
                    if not team_data.empty:
                        comparison_data.append(team_data.iloc[0])
                
                if comparison_data:
                    comparison_df = pd.DataFrame(comparison_data)
                    st.dataframe(comparison_df, use_container_width=True, hide_index=True)
        
        elif analysis_type == "Player Comparison":
            st.subheader("Compare Top Scorers")
            top_scorers = get_top_scorers(engine, limit=15)
            
            if not top_scorers.empty:
                st.dataframe(top_scorers, use_container_width=True, hide_index=True)
                
                # Comparison chart
                fig = px.bar(
                    top_scorers.head(10),
                    x='nom_joueur',
                    y=['total_goals', 'total_assists'],
                    title='Top 10 Players: Goals vs Assists',
                    labels={'value': 'Count', 'nom_joueur': 'Player'},
                    barmode='group'
                )
                st.plotly_chart(fig, use_container_width=True)
        
        elif analysis_type == "Goal Trends":
            st.subheader("Goals Scored Trends")
            match_data = get_match_data(engine)
            
            if not match_data.empty:
                # Convert date to datetime
                match_data['date_match'] = pd.to_datetime(match_data['date_match'])
                match_data = match_data.sort_values('date_match')
                
                # Calculate cumulative goals
                match_data['cumulative_goals'] = (match_data['buts_domicile'] + match_data['buts_exterieur']).cumsum()
                
                # Line chart
                fig = px.line(
                    match_data,
                    x='date_match',
                    y='cumulative_goals',
                    title='Cumulative Goals Over Season',
                    labels={'cumulative_goals': 'Total Goals', 'date_match': 'Date'}
                )
                st.plotly_chart(fig, use_container_width=True)
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("📊 Dashboard v1.0 | Last Updated: 2024")
    st.sidebar.markdown("Data Source: FBref | Database: PostgreSQL")

if __name__ == "__main__":
    main()
