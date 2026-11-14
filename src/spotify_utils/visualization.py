import plotly.express as px
import plotly.graph_objects as go


def plot_artist_distribution(
    distribution,
):
    fig = px.pie(
        names=list(distribution.keys()),
        values=list(distribution.values()),
        title="Artist listening distribution",
    )
    fig.show()


def plot_discovery_rate(monthly_data):
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=[item["month"] for item in monthly_data],
            y=[item["song_rate"] for item in monthly_data],
            mode="lines+markers",
            name="Songs",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=[item["month"] for item in monthly_data],
            y=[item["artist_rate"] for item in monthly_data],
            mode="lines+markers",
            name="Artists",
        )
    )

    fig.update_layout(
        title="Discovery Rate Over Time",
        xaxis_title="Month",
        yaxis_title="Discovery Rate",
        yaxis_tickformat=".0%",
        yaxis_range=[0, 1],
        hovermode="x unified",
    )

    fig.show()


def plot_discovery_counts(monthly_data):
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=[item["month"] for item in monthly_data],
            y=[item["new_songs"] for item in monthly_data],
            mode="lines+markers",
            name="New Songs",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=[item["month"] for item in monthly_data],
            y=[item["new_artists"] for item in monthly_data],
            mode="lines+markers",
            name="New Artists",
        )
    )

    fig.update_layout(
        title="Discoveries Over Time",
        xaxis_title="Month",
        yaxis_title="Number of Discoveries",
        hovermode="x unified",
    )

    fig.show()
