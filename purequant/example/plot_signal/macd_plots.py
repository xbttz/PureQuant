import pandas as pd
import finplot as fplt
from purequant.indicators import INDICATORS
from purequant.config import config
from purequant.trade import HUOBISWAP
from purequant.logger import logger

class Kline:

    def __init__(self):
        config.loads('config.json')
        self.symbol = "BTC-USD-SWAP"
        self.timeframe = "1m"
        self.exchange = HUOBISWAP("", "", self.symbol)
        self.indicators = INDICATORS(self.exchange, self.symbol, self.timeframe)


    def update(self):
        table = self.exchange.get_kline(self.timeframe)
        table.reverse()
        try:
            df = pd.DataFrame(table, columns='time open high low close volume currency_volume'.split())
            df = df.astype({'time': 'datetime64[ns]', 'open': 'float64', 'high': 'float64', 'low': 'float64',
                            'close': 'float64', 'volume': 'float64', 'currency_volume': 'float64'})
        except:
            df = pd.DataFrame(table, columns='time open high low close volume'.split())
            df = df.astype(
                {'time': 'datetime64[ns]', 'open': 'float64', 'high': 'float64',
                 'low': 'float64', 'close': 'float64', 'volume': 'float64'})
        candlesticks = df['time open close high low'.split()]
        volumes = df['time open close volume'.split()]
        result = self.indicators.MACD(12, 26, 9)
        dif = result['DIF']
        dea = result['DEA']
        macd = result['MACD']
        if not plots:
            # first time we create the plots
            global ax, ax2, ax3
            plots.append(fplt.candlestick_ochl(candlesticks))
            plots.append(fplt.volume_ocv(volumes, ax=ax2))
            plots.append(fplt.plot(dif, ax=ax3, legend="DIF"))
            plots.append(fplt.plot(dea, ax=ax3, legend="DEA"))
            plots.append(fplt.plot(macd, ax=ax3, legend="MACD"))
        else:
            # every time after we just update the data sources on each plot
            plots[0].update_data(candlesticks)
            plots[1].update_data(volumes)
            plots[2].update_data(dif)
            plots[3].update_data(dea)
            plots[4].update_data(macd)

if __name__ == "__main__":
    try:
        kline = Kline()
        plots = []
        fplt.foreground = '#FFFFFF'  # 前景色
        fplt.background = '#333333'  # 背景色
        fplt.odd_plot_background = '#333333'  # 第二层图纸的背景色
        fplt.cross_hair_color = "#FFFFFF"  # 准星的颜色
        ax, ax2, ax3 = fplt.create_plot('Realtime kline', init_zoom_periods=100, maximize=False, rows=3)
        fplt.add_legend("VOLUME", ax2)  # 增加"VOLUME"图例
        kline.update()
        fplt.timer_callback(kline.update, 5.0)  # update (using synchronous rest call) every N seconds
        fplt.show()
    except:
        logger.error()