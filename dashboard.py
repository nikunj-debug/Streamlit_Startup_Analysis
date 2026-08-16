import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
#import seaborn as sns

st.set_page_config(layout='wide',page_title='StartUp Analysis')  # print the name on the tab of streamlit

# All the eiditing part performed on the dataset to improve the results
df = pd.read_csv('startup_cleaned.csv')
df['date'] = pd.to_datetime(df['date'],errors='coerce')
df['month'] = df['date'].dt.month
df['year'] = df['date'].dt.year
df['city'] = df['city'].replace({'Bengaluru': 'Bangalore', 'Gurgaon': 'Gurugram', 'New Delhi': 'Delhi'})
df['startup']=df['startup'].replace({'Flipkart.com':'Flipkart','Ola Cabs':'Ola','Olacabs':'Ola','Rapido Bike Taxi':'Rapido','Oyo Rooms':'OYO Rooms'})
df['investors']=df['investors'].replace({'SoftBank Group':'Softbank'})


def load_overall_analysis():
    st.title('Overall Analysis')

    # total invested amount
    total = round(df['amount'].sum())
    # max amount infused in a startup
    max_funding = df.groupby('startup')['amount'].max().sort_values(ascending=False).head(1).values[0]
    # avg ticket size
    avg_funding = df.groupby('startup')['amount'].sum().mean()
    # total funded startups
    num_startups = df['startup'].nunique()

    col1,col2,col3,col4 = st.columns(4)

    with col1:
        st.metric('Total',str(total) + ' Cr')
    with col2:
        st.metric('Max', str(max_funding) + ' Cr')

    with col3:
        st.metric('Avg',str(round(avg_funding)) + ' Cr')

    with col4:
        st.metric('Funded Startups',num_startups)

    st.header('MoM Graph')
    selected_option = st.selectbox('Select Type',['Total','Count'])
    if selected_option == 'Total':
        temp_df = df.groupby(['year','month'])['amount'].sum().reset_index()
    else:
        temp_df = df.groupby(['year','month'])['amount'].count().reset_index()

    #temp_df['x_axis'] = temp_df['year'].astype('str')
    temp_df['x_axis'] = pd.to_datetime(temp_df[['year', 'month']].assign(day=20))
    

    fig4, ax = plt.subplots(figsize=(12, 5))

    ax.plot(
        temp_df['x_axis'],
        temp_df['amount']
    )

    ax.set_xlabel('Date')
    ax.set_ylabel(
        'Monthly Investment' if selected_option == 'Total'
        else 'Number of Investments'
    )
    ax.grid(True, alpha=0.3)
    fig4.autofmt_xdate()
    st.pyplot(fig4)

    # Adding the city wise funding analysis 
    st.header('City wise')

    
    co1,co2=st.columns(2)

    with co1:
        st.subheader('City Wise Deals')
        #city_wise_fund=df.groupby('city')['amount'].sum().sort_values(ascending=False).head(7)
        city_wise_deals=df['city'].value_counts().head(7)
        fig5, ax1 = plt.subplots()
        ax1.pie(city_wise_deals,labels=city_wise_deals.index,autopct="%0.01f%%")
        
        st.pyplot(fig5)

        


        
    with co2:
        st.subheader('City Wise Amount Funded')



        city_wise_fund = df.groupby('city')['amount'].sum().sort_values(ascending=False).head(7).reset_index()

        # 2. Create an interactive horizontal bar chart
        # Horizontal bars are much better for city names to prevent vertical/overlapping text
        fig6 = px.bar(
    city_wise_fund,
    x='city',
    y='amount',
    text='city',  # Adds data labels on top of the bar
    color='amount',  # Creates a visual gradient based on height
    color_continuous_scale='Reds'
)
        fig6.update_traces(textposition='outside')



        fig6.update_layout(
            yaxis_title="Total Amount Funded (Cr)",
            xaxis_title="City",
            coloraxis_showscale=False,  # Hides the color gradient legend bar for a cleaner look
            height=400,
            
        )
        fig6.update_xaxes(showticklabels=False) 

        # 4. Render the interactive Plotly chart in Streamlit
        st.plotly_chart(fig6, use_container_width=True)


        #st.markdown("---")

        # Data Insight Pointers using Markdown
    with st.expander("## 📊 Key Insights: Volume vs. Value Disparity"):
            st.markdown("""
            ### 📊 Key Insights: Volume vs. Value Disparity

            * **Deal Concentration:** The vast majority of startup deals are heavily concentrated in **Mumbai** and **Bangalore**, showing that these cities host the highest volume of active investment activity.
            * **The Funding Gap:** While both cities dominate the chart in terms of *number* of transactions, there is an **immense difference** in the *total amount funded*. 
            * **High-Value Outliers:** One of these hubs secures significantly larger, late-stage mega-rounds. This causes its total funding value to skyrocket far past the other, despite having a similar volume of individual deals.
            """)



    #top startups analysis

    st.subheader('Top Startup')

    top_startups = (
    df.groupby(['year', 'startup'])['amount']
    .sum()
    .reset_index()
    .sort_values(by=['year', 'amount'], ascending=False)
    .drop_duplicates(subset=['year'])
    .sort_values(by='year') ) # Sort chronologically for better plotting

          #or it can be done using idxmax()

           # Group by year and find the row index with the maximum amount for each year
           #max_per_year_idx = df.groupby('year')['amount'].idxmax()
           #max_per_year = df.loc[max_per_year_idx]
           #max_per_year[['year', 'startup', 'amount']].sort_values(by='year', ascending=False)'''

    st.subheader("Top Funded Startup Per Year")
 
    # to present the top funded startup per year in table 
    st.dataframe(top_startups, use_container_width=True,hide_index=True)


    # to present the top funded startup per year in graph form  

    hidden_code_block = """fig7 = px.bar(
    top_startups,
    x='year',
    y='amount',
    hover_name='startup',
    text='startup',
    title='Top Funded Startup Per Year',
    labels={'year': 'Year', 'amount': 'Amount'})

    fig7.update_traces(textposition='outside')
    fig7.update_layout(yaxis={'categoryorder': 'total descending'})

    st.plotly_chart(fig7, use_container_width=True)"""

    # each startup's overall fundings 
    

    total_fund=df.groupby('startup')['amount'].sum().sort_values(ascending=False).head(10)
    fig8 = px.bar(
        total_fund,
        x=total_fund.index,
        y=total_fund.values,
        #hover_name='startup',
        #text='startup',
        title='Top Funded Startup',
        )
    
    fig8.update_traces(text=total_fund.index,textposition='outside')

    fig8.update_xaxes(showticklabels=False)
    fig8.update_layout(
    xaxis_title="Startups",
    yaxis_title="Total Amount Raised"
)
    
    st.plotly_chart(fig8, use_container_width=True)
    with st.expander('🚀 Capital Overview: Top Funded Startups'):
        st.markdown("""
    ### 🚀 Capital Overview: Top Funded Startups

    * **Ecosystem Scale:** The overall funding landscape showcases massive capital injection, heavily driven by late-stage mega-rounds that significantly elevate the ecosystem's total value.
    * **The Dominant Players:** A select group of elite startups captures the lion's share of total capital. These market leaders skew the averages, out-funding hundreds of early-stage competitors combined.
    * **Valuation Movers:** The top startups highlighted here aren't just raising capital to survive; their massive funding rounds dictate overall market velocity, investor confidence, and sector trends for the entire year.
    """)
    

    #Top investors 

    top_investor=df.groupby('investors')['amount'].sum().sort_values(ascending=False).head(5)

    fig9 = px.bar(
            top_investor,
            x=top_investor.index,
            y=top_investor.values,
            #hover_name='startup',
            #text='startup',
            title='Top Investros',
            )
        
    fig9.update_traces(text=top_investor.index,textposition='outside')
    
    fig9.update_xaxes(showticklabels=False)
    fig9.update_layout(
        xaxis_title="Startups",
        yaxis_title="Total Amount Raised"
    )
        
    st.plotly_chart(fig9, use_container_width=False)

# Heatmap

    # Create a pivot table
    funding_pivot = df.pivot_table(
        index='year', 
        columns='month', 
        values='amount', 
        aggfunc='sum', 
        fill_value=0
    )

    # Plot interactive heatmap
    fig10 = px.imshow(
        funding_pivot,
        labels=dict(x="Month", y="Year", color="Total Amount"),
        x=funding_pivot.columns,
        y=funding_pivot.index,
        color_continuous_scale='Viridis',
        title="Funding Heatmap (Year vs Month)"
    )

    # Display in Streamlit:
    # st.plotly_chart(fig, use_container_width=True)

    st.plotly_chart(fig10, use_container_width=True)
    with st.expander(' 📅 Macro Trends: Funding Seasonality Heatmap'):
            st.markdown("""
    ### 📅 Macro Trends: Funding Seasonality Heatmap

    * **Spotting Hotspots:** The color intensity instantly isolates peak funding periods. Deeper or brighter blocks reveal specific months where massive mega-deals or high-volume rounds shifted market velocity.
    * **Temporal Patterns:** This matrix allows you to trace horizontal rows to evaluate **year-over-year performance**, or scan vertical columns to identify **recurring seasonal trends** (e.g., historical Q1 surges vs. Q4 funding slowdowns).
    * **Market Shift Tracking:** Sudden transitions across the grid map out macro-economic transitions clearly—making it easy to see exactly when the ecosystem moved from a capital surplus into a funding winter.
    """)
        
def load_investor_details(investor):
    st.title(investor)
    # load the recent 5 investments of the investor
    last5_df = df[df['investors'].str.contains(investor)][['date', 'startup', 'vertical', 'city', 'round', 'amount']]
    #sorting on the basis of date to get most recent investements
    last5_df=last5_df.sort_values(by='date',ascending=False)
    st.subheader('Most Recent Investments')
    st.dataframe(last5_df.head(),use_container_width=True,hide_index=True)

    st.metric('Generally invested vertical is',last5_df['vertical'].mode()[0])

    # sector invested with most amounts
    st.subheader('Most Amount Invested Vertical')
    st.write(last5_df.groupby('vertical')['amount'].sum().sort_values(ascending=False).head())

    col1, col2 = st.columns(2)
    with col1:
        # biggest investments
        big_series = df[df['investors'].str.contains(investor)].groupby('startup')['amount'].sum().sort_values(ascending=False).head()
        st.subheader('Biggest Investments')
        fig, ax = plt.subplots()
        ax.bar(big_series.index,big_series.values)

        st.pyplot(fig)

    with col2:
        verical_series = df[df['investors'].str.contains(investor)].groupby('vertical')['amount'].sum()

        st.subheader('Sectors invested in')
        fig1, ax1 = plt.subplots()
        ax1.pie(verical_series,labels=verical_series.index,autopct="%0.01f%%")

        st.pyplot(fig1)

    #print(df.info())
    co3,co4 = st.columns(2)

    with co3:

        #df['year'] = df['date'].dt.year
        
        year = df[df['investors'].str.contains(investor)].groupby('year')['amount'].sum().reset_index()

        year['x_axis'] = year['year'].astype('str')

        st.subheader('YoY Investment')
        fig2, ax2 = plt.subplots()
        ax2.plot(year['x_axis'],year['amount'])

        ax2.set_xlabel('Year')
        ax2.set_ylabel(
                'Total Investment'
            )

        st.pyplot(fig2)
    with co4:

        st.subheader('City Investement')

        city=last5_df.groupby('city')['amount'].sum()
        fig4, ax4 = plt.subplots()
        ax4.pie(city,labels=city.index,autopct="%0.01f%%")
        
        st.pyplot(fig4)

def load_startup(company):
    st.title(company)
    #st.subheader('Vertical of '+ company)
    #st.write(df[df['startup']==company]['vertical'].values[0])

    startup_data = df[df['startup'] == company].iloc[0]
    
    # Divide into columns for a key-value layout
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.caption("INDUSTRY VERTICAL")
        st.subheader(f"🏷️ {startup_data['vertical']}")
        
    with col2:
        st.caption("SUB-VERTICAL")
        st.subheader(f"📌 {startup_data.get('subvertical', 'N/A')}")

    with col3:
        st.caption("LOCATION")
        st.subheader(f"📍 {startup_data.get('city', 'N/A')}")
        
    st.divider() # Creates a clean horizontal line

#funding rounds of startups
    
    rounds=df[df['startup']==company][['year','round','investors','amount']]

    st.subheader('Funding Rounds')
    st.dataframe(rounds, use_container_width=True,hide_index=True)

    st.metric('Total Funding raised',rounds['amount'].sum())

#similiar companies

    similar_vertical=df[startup_data['subvertical']==df['subvertical']]

    st.subheader('Similiar Companies')
    st.dataframe(similar_vertical[['year','startup','vertical','investors','amount']],use_container_width=True,hide_index=True)


st.sidebar.title('Startup Funding Analysis')

option = st.sidebar.selectbox('Select One',['Overall Analysis','StartUp','Investor'])

if option == 'Overall Analysis':
    load_overall_analysis()

elif option == 'StartUp':
    st.title('StartUp Analysis')

    selected_startup = st.sidebar.selectbox('Select StartUp',sorted(df['startup'].unique().tolist()))
   
    btn1 = st.sidebar.button('Find StartUp Details')
    if btn1:
        load_startup(selected_startup)
    
else:
    selected_investor = st.sidebar.selectbox('Select StartUp',sorted(set(df['investors'].str.split(',').sum())))
    btn2 = st.sidebar.button('Find Investor Details')
    if btn2:
        load_investor_details(selected_investor)

