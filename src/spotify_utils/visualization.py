import plotly.express as px


def plot_artist_distribution(
    distribution,
):
    fig = px.pie(
        names=list(distribution.keys()),
        values=list(distribution.values()),
        title="Artist listening distribution",
    )
    fig.show()
