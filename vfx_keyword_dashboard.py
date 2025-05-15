import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import re
from io import BytesIO

# Set page configuration
st.set_page_config(
    page_title="VFX Studio Keyword Analytics Dashboard",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        margin-bottom: 1rem;
    }
    .section-header {
        font-size: 1.8rem;
        color: #0D47A1;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .subsection-header {
        font-size: 1.4rem;
        color: #1565C0;
        margin-top: 1.5rem;
        margin-bottom: 0.8rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #1E88E5;
    }
    .metric-label {
        font-size: 1rem;
        color: #424242;
    }
    .highlight {
        background-color: #e3f2fd;
        padding: 0.5rem;
        border-radius: 5px;
        margin-bottom: 1rem;
    }
    .footer {
        margin-top: 3rem;
        text-align: center;
        color: #757575;
    }
</style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("keywords_with_intent.csv")
    return df

# Function to generate downloadable link
def get_download_link(df, filename, link_text):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{link_text}</a>'
    return href

# Function to convert dataframe to Excel
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Keywords')
    processed_data = output.getvalue()
    return processed_data

# Main app
def main():
    # Header
    st.markdown('<div class="main-header">VFX Studio Keyword Analytics Dashboard</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="highlight">
    This dashboard helps VFX studios analyze and prioritize keywords by search intent and CPC viability. 
    Use the filters to explore different segments of the keyword data and identify high-value targeting opportunities.
    </div>
    """, unsafe_allow_html=True)
    
    # Load data
    try:
        df = load_data()
        st.success(f"Successfully loaded {len(df)} keywords with search intent classification.")
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return
    
    # Sidebar filters
    st.sidebar.markdown("## Filters")
    
    # Intent filter
    intent_options = ['All'] + sorted(df['search_intent'].unique().tolist())
    selected_intent = st.sidebar.selectbox('Search Intent', intent_options)
    
    # Volume range filter
    min_volume = int(df['avg_monthly_searches'].min())
    max_volume = int(df['avg_monthly_searches'].max())
    volume_range = st.sidebar.slider('Monthly Search Volume', min_volume, max_volume, (min_volume, max_volume))
    
    # CPC range filter
    min_cpc = float(df['cpc'].min())
    max_cpc = float(df['cpc'].max())
    cpc_range = st.sidebar.slider('Cost Per Click (CPC)', min_cpc, max_cpc, (min_cpc, max_cpc))
    
    # Competition score filter
    min_comp = float(df['competition_score'].min())
    max_comp = float(df['competition_score'].max())
    competition_range = st.sidebar.slider('Competition Score', min_comp, max_comp, (min_comp, max_comp))
    
    # Keyword text filter
    keyword_filter = st.sidebar.text_input('Keyword Contains')
    
    # Apply filters
    filtered_df = df.copy()
    
    if selected_intent != 'All':
        filtered_df = filtered_df[filtered_df['search_intent'] == selected_intent]
    
    filtered_df = filtered_df[
        (filtered_df['avg_monthly_searches'] >= volume_range[0]) & 
        (filtered_df['avg_monthly_searches'] <= volume_range[1]) &
        (filtered_df['cpc'] >= cpc_range[0]) & 
        (filtered_df['cpc'] <= cpc_range[1]) &
        (filtered_df['competition_score'] >= competition_range[0]) & 
        (filtered_df['competition_score'] <= competition_range[1])
    ]
    
    if keyword_filter:
        filtered_df = filtered_df[filtered_df['keyword'].str.contains(keyword_filter, case=False)]
    
    # Display filter summary
    st.markdown('<div class="subsection-header">Filter Summary</div>', unsafe_allow_html=True)
    st.write(f"Showing {len(filtered_df)} of {len(df)} keywords ({(len(filtered_df)/len(df)*100):.1f}%)")
    
    # Summary Metrics Section
    st.markdown('<div class="section-header">Summary Metrics</div>', unsafe_allow_html=True)
    
    # Create metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Total Keywords</div>
            <div class="metric-value">{:,}</div>
        </div>
        """.format(len(filtered_df)), unsafe_allow_html=True)
    
    with col2:
        avg_volume = filtered_df['avg_monthly_searches'].mean()
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Avg. Monthly Searches</div>
            <div class="metric-value">{:,.1f}</div>
        </div>
        """.format(avg_volume), unsafe_allow_html=True)
    
    with col3:
        avg_cpc = filtered_df['cpc'].mean()
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Avg. CPC</div>
            <div class="metric-value">${:,.2f}</div>
        </div>
        """.format(avg_cpc), unsafe_allow_html=True)
    
    with col4:
        avg_competition = filtered_df['competition_score'].mean()
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Avg. Competition Score</div>
            <div class="metric-value">{:,.1f}</div>
        </div>
        """.format(avg_competition), unsafe_allow_html=True)
    
    # Intent breakdown
    st.markdown('<div class="subsection-header">Intent Breakdown</div>', unsafe_allow_html=True)
    
    intent_counts = filtered_df['search_intent'].value_counts().reset_index()
    intent_counts.columns = ['Intent', 'Count']
    
    # Intent metrics by row
    intent_metrics = filtered_df.groupby('search_intent').agg({
        'avg_monthly_searches': 'mean',
        'cpc': 'mean',
        'competition_score': 'mean'
    }).reset_index()
    
    intent_metrics.columns = ['Intent', 'Avg. Monthly Searches', 'Avg. CPC', 'Avg. Competition']
    
    # Merge the two dataframes
    intent_summary = pd.merge(intent_counts, intent_metrics, on='Intent')
    
    # Display the intent summary
    st.dataframe(intent_summary.style.format({
        'Avg. Monthly Searches': '{:,.1f}',
        'Avg. CPC': '${:,.2f}',
        'Avg. Competition': '{:,.1f}'
    }))
    
    # Visual Charts Section
    st.markdown('<div class="section-header">Visual Charts</div>', unsafe_allow_html=True)
    
    # Create tabs for different visualizations
    tab1, tab2, tab3, tab4 = st.tabs(["Volume by Intent", "CPC vs Volume", "Keyword Clusters", "Top Keywords"])
    
    with tab1:
        # Bar chart of total monthly volume by intent
        intent_volume = filtered_df.groupby('search_intent')['avg_monthly_searches'].sum().reset_index()
        fig1 = px.bar(
            intent_volume, 
            x='search_intent', 
            y='avg_monthly_searches',
            color='search_intent',
            labels={'search_intent': 'Search Intent', 'avg_monthly_searches': 'Total Monthly Search Volume'},
            title='Total Monthly Search Volume by Intent'
        )
        st.plotly_chart(fig1, use_container_width=True)
        
        st.markdown("""
        <div class="highlight">
        <strong>Insight:</strong> This chart shows the total search volume distribution across different intent categories.
        Higher volume categories represent larger audience segments that could be targeted.
        </div>
        """, unsafe_allow_html=True)
    
    with tab2:
        # Scatter plot of CPC vs. search volume, colored by competition score
        fig2 = px.scatter(
            filtered_df, 
            x='avg_monthly_searches', 
            y='cpc',
            color='competition_score',
            size='avg_monthly_searches',
            hover_name='keyword',
            color_continuous_scale='Viridis',
            labels={
                'avg_monthly_searches': 'Average Monthly Searches',
                'cpc': 'Cost Per Click ($)',
                'competition_score': 'Competition Score'
            },
            title='CPC vs. Search Volume (colored by Competition Score)'
        )
        st.plotly_chart(fig2, use_container_width=True)
        
        st.markdown("""
        <div class="highlight">
        <strong>Insight:</strong> This visualization helps identify high-volume, low-competition keywords with reasonable CPCs.
        The ideal targets are often in the upper-right quadrant with lighter colors (lower competition).
        </div>
        """, unsafe_allow_html=True)
    
    with tab3:
        # Extract keyword clusters based on common terms
        def extract_main_terms(keyword):
            # Remove common words and keep main terms
            common_words = ['and', 'the', 'for', 'with', 'in', 'on', 'of', 'to', 'a']
            terms = keyword.lower().split()
            return ' '.join([term for term in terms if term not in common_words and len(term) > 2])
        
        filtered_df['main_terms'] = filtered_df['keyword'].apply(extract_main_terms)
        
        # Get the most common terms
        all_terms = ' '.join(filtered_df['main_terms']).split()
        term_counts = pd.Series(all_terms).value_counts().head(20)
        
        # Create a treemap of keyword clusters
        term_df = pd.DataFrame({'term': term_counts.index, 'count': term_counts.values})
        
        fig3 = px.treemap(
            term_df,
            path=['term'],
            values='count',
            color='count',
            color_continuous_scale='RdBu',
            title='Keyword Clusters by Common Terms'
        )
        st.plotly_chart(fig3, use_container_width=True)
        
        st.markdown("""
        <div class="highlight">
        <strong>Insight:</strong> This treemap shows the most common terms in your keyword set, helping identify major topic clusters.
        Larger blocks represent more frequently occurring terms that could form the basis of content themes.
        </div>
        """, unsafe_allow_html=True)
    
    with tab4:
        # Top 20 high-volume/high-CPC keywords
        st.markdown('<div class="subsection-header">Top 20 High-Value Keywords</div>', unsafe_allow_html=True)
        
        # Create a value score (volume * CPC)
        filtered_df['value_score'] = filtered_df['avg_monthly_searches'] * filtered_df['cpc']
        
        # Get top 20 by value score
        top_keywords = filtered_df.sort_values('value_score', ascending=False).head(20)
        
        # Display as a table
        st.dataframe(
            top_keywords[['keyword', 'search_intent', 'avg_monthly_searches', 'cpc', 'competition_score', 'value_score']]
            .style.format({
                'avg_monthly_searches': '{:,.0f}',
                'cpc': '${:,.2f}',
                'competition_score': '{:,.1f}',
                'value_score': '{:,.0f}'
            })
        )
        
        st.markdown("""
        <div class="highlight">
        <strong>Insight:</strong> These keywords represent the highest potential value based on a combination of search volume and CPC.
        They should be prioritized in your targeting strategy, especially those with lower competition scores.
        </div>
        """, unsafe_allow_html=True)
    
    # Data Table Section
    st.markdown('<div class="section-header">Keyword Data Table</div>', unsafe_allow_html=True)
    
    # Sorting options
    sort_options = {
        'Keyword (A-Z)': ('keyword', False),
        'Keyword (Z-A)': ('keyword', True),
        'Highest Search Volume': ('avg_monthly_searches', True),
        'Lowest Search Volume': ('avg_monthly_searches', False),
        'Highest CPC': ('cpc', True),
        'Lowest CPC': ('cpc', False),
        'Highest Competition': ('competition_score', True),
        'Lowest Competition': ('competition_score', False)
    }
    
    sort_by = st.selectbox('Sort by', list(sort_options.keys()))
    sort_col, sort_ascending = sort_options[sort_by]
    
    # Sort the dataframe
    sorted_df = filtered_df.sort_values(by=sort_col, ascending=sort_ascending)
    
    # Display the dataframe
    st.dataframe(
        sorted_df[['keyword', 'search_intent', 'avg_monthly_searches', 'cpc', 'competition_score', 'competition_text']]
        .style.format({
            'avg_monthly_searches': '{:,.0f}',
            'cpc': '${:,.2f}',
            'competition_score': '{:,.1f}'
        })
    )
    
    # Export Section
    st.markdown('<div class="section-header">Export Data</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # CSV export
        csv = sorted_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download as CSV",
            data=csv,
            file_name="vfx_keywords_export.csv",
            mime="text/csv"
        )
    
    with col2:
        # Excel export
        excel_data = to_excel(sorted_df)
        st.download_button(
            label="Download as Excel",
            data=excel_data,
            file_name="vfx_keywords_export.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    # Footer
    st.markdown("""
    <div class="footer">
        <p>VFX Studio Keyword Analytics Dashboard | Created for boutique VFX studios targeting brand-side marketers</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
