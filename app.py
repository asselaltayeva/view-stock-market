import flet as ft
import requests
from config import API_KEY


def main(page: ft.Page):
    # App settings
    page.title = "Stock market"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20
    page.window_width = 1000
    page.window_height = 700

    # state refs
    stock_symbol = ft.Ref[ft.TextField]()
    chart_container = ft.Ref[ft.Container]()
    price_info = ft.Ref[ft.Container]()
    price_text_below = ft.Ref[ft.Container]()
    error_messages = ft.Ref[ft.Container]()
    time_range_dropdown = ft.Ref[ft.Dropdown]()

    # time range helpers
    def get_days_for_range(range_name):
        ranges = {
            "1 week": 7,
            "2 weeks": 14,
            "30 days": 30,
            "90 days": 90,
            "1 year": 365,
            "5 years": 1825,
        }
        return ranges.get(range_name, 30)

    def get_range_label(range_name):
        return range_name

    # fetch stock data
    def fetch_stock_data(e):
        symbol = stock_symbol.current.value.upper().strip()
        time_range = time_range_dropdown.current.value or "30 days"
        days = get_days_for_range(time_range)

        if not symbol:
            error_messages.current.content = ft.Text(
                "Please enter a stock symbol.",
                color=ft.colors.RED,
                size=14,
            )
            error_messages.current.visible = True
            price_info.current.visible = False
            price_text_below.current.visible = False
            chart_container.current.visible = False
            page.update()
            return

        error_messages.current.visible = False

        chart_container.current.content = ft.Text(
            "Loading...", size=16, color=ft.colors.BLUE
        )
        chart_container.current.visible = True
        page.update()

        try:
            url = (
                "https://www.alphavantage.co/query"
                f"?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={API_KEY}"
            )
            response = requests.get(url)
            data = response.json()

            time_series = data["Time Series (Daily)"]

            dates = sorted(time_series.keys(), reverse=True)[:days]
            dates.reverse()

            closes = []
            for date in dates:
                closes.append(float(time_series[date]["4. close"]))

            latest_date = sorted(time_series.keys(), reverse=True)[0]
            latest_data = time_series[latest_date]

            # price info
            price_info.current.content = ft.Column(
                [
                    ft.Text(
                        f"Stock: {symbol}",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.BLUE_700,
                    ),
                    ft.Text(
                        f"Date: {latest_date}",
                        size=14,
                        color=ft.colors.GREY_700,
                    ),
                    ft.Divider(),
                    ft.Row(
                        [
                            _price_box(
                                "Open",
                                latest_data["1. open"],
                                ft.colors.BLUE_900,
                                ft.colors.BLUE_50,
                            ),
                            _price_box(
                                "High",
                                latest_data["2. high"],
                                ft.colors.GREEN_900,
                                ft.colors.GREEN_50,
                            ),
                            _price_box(
                                "Low",
                                latest_data["3. low"],
                                ft.colors.RED_900,
                                ft.colors.RED_50,
                            ),
                            _price_box(
                                "Close",
                                latest_data["4. close"],
                                ft.colors.PURPLE_900,
                                ft.colors.PURPLE_50,
                            ),
                        ],
                        spacing=10,
                    ),
                ]
            )
            price_info.current.visible = True

            chart = ft.LineChart(
                data_series=[
                    ft.LineChartData(
                        data_points=[
                            ft.LineChartDataPoint(i, closes[i])
                            for i in range(len(closes))
                        ],
                        stroke_width=3,
                        color=ft.colors.BLUE,
                        below_line_bgcolor=ft.colors.BLUE_50,
                    )
                ],
                min_x=0,
                max_x=len(closes) - 1,
                min_y=min(closes) * 0.95,
                max_y=max(closes) * 1.05,
                expand=True,
            )

            chart_container.current.content = ft.Container(
                content=ft.Column(
                    [
                        ft.Text(
                            f"Closing Prices - {get_range_label(time_range)}",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                        ),
                        chart,
                    ],
                    spacing=10,
                ),
                padding=15,
                border=ft.border.all(2, ft.colors.GREY_300),
                border_radius=10,
            )
            chart_container.current.visible = True

            price_text_below.current.content = ft.Text(
                f"Open: ${float(latest_data['1. open']):.2f} | "
                f"High: ${float(latest_data['2. high']):.2f} | "
                f"Low: ${float(latest_data['3. low']):.2f} | "
                f"Close: ${float(latest_data['4. close']):.2f}",
                size=16,
                weight=ft.FontWeight.BOLD,
                text_align=ft.TextAlign.CENTER,
            )
            price_text_below.current.visible = True

        except Exception:
            error_messages.current.content = ft.Text(
                "Error fetching data. Please try again.",
                color=ft.colors.RED,
                size=14,
            )
            error_messages.current.visible = True
            price_info.current.visible = False
            price_text_below.current.visible = False
            chart_container.current.visible = False

        page.update()

    def _price_box(title, value, text_color, bg_color):
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(title, size=12, color=ft.colors.GREY_600),
                    ft.Text(
                        f"${float(value):.2f}",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=text_color,
                    ),
                ],
                spacing=5,
            ),
            padding=15,
            bgcolor=bg_color,
            border_radius=10,
            expand=True,
        )

    # layout
    page.add(
        ft.Column(
            [
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text("View Stock Market Data", size=22),
                            ft.Text(
                                "Enter a stock symbol to fetch its latest market data."
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=ft.padding.only(bottom=20),
                ),
                ft.Container(
                    content=ft.Row(
                        [
                            ft.TextField(
                                ref=stock_symbol,
                                label="Stock Symbol",
                                width=300,
                                on_submit=fetch_stock_data,
                            ),
                            ft.Dropdown(
                                ref=time_range_dropdown,
                                label="Time Range",
                                width=150,
                                options=[
                                    ft.dropdown.Option("1 week"),
                                    ft.dropdown.Option("2 weeks"),
                                    ft.dropdown.Option("30 days"),
                                    ft.dropdown.Option("90 days"),
                                    ft.dropdown.Option("1 year"),
                                    ft.dropdown.Option("5 years"),
                                ],
                                value="30 days",
                            ),
                            ft.ElevatedButton(
                                "Get Stock Data",
                                icon=ft.icons.SEARCH,
                                on_click=fetch_stock_data,
                            ),
                        ],
                        spacing=10,
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                ),
                ft.Container(ref=error_messages,padding=10, visible=False),
                ft.Container(ref=price_info, padding=10, visible=False),
                ft.Container(ref=chart_container, padding=10, visible=False),
                ft.Container(ref=price_text_below, padding=10, visible=False),
            ], spacing=15
        )
    )
    if __name__ == "__main__":
        ft.app(target=main)
