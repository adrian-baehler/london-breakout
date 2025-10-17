"""
cTrader Open API Integration Module

This module provides integration with cTrader for live trading.
Requires OpenApiPy package: pip install git+https://github.com/spotware/OpenApiPy.git

Note: This is a template/framework. You'll need to install OpenApiPy and
configure your cTrader credentials to use live trading.
"""
import os
from typing import Optional, Callable, Dict, List
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Try to import OpenApiPy (may not be installed yet)
try:
    from OpenApiPy import Client, Helpers, TcpProtocol
    from OpenApiPy.messages.OpenApiCommonMessages_pb2 import *
    from OpenApiPy.messages.OpenApiMessages_pb2 import *
    CTRADER_AVAILABLE = True
except ImportError:
    CTRADER_AVAILABLE = False
    print("WARNING: OpenApiPy not installed. Install with:")
    print("pip install git+https://github.com/spotware/OpenApiPy.git")

import config


class CTraderClient:
    """
    Wrapper for cTrader Open API Client

    Features:
    - Connection management with auto-reconnect
    - Market data streaming
    - Order execution (market and limit orders)
    - Position monitoring
    - Account information
    """

    def __init__(self):
        if not CTRADER_AVAILABLE:
            raise ImportError("OpenApiPy is not installed. Cannot use cTrader API.")

        # Load credentials from environment or config
        self.client_id = os.getenv('CTRADER_CLIENT_ID') or config.CLIENT_ID
        self.client_secret = os.getenv('CTRADER_CLIENT_SECRET') or config.CLIENT_SECRET
        self.access_token = os.getenv('CTRADER_ACCESS_TOKEN') or config.ACCESS_TOKEN
        self.account_id = os.getenv('CTRADER_ACCOUNT_ID') or config.ACCOUNT_ID

        self.host = os.getenv('CTRADER_HOST') or config.CTRADER_HOST
        self.port = int(os.getenv('CTRADER_PORT', config.CTRADER_PORT))

        # Validate credentials
        if not all([self.client_id, self.client_secret, self.access_token, self.account_id]):
            raise ValueError(
                "Missing cTrader credentials. Set them in .env file or config.py\n"
                "Required: CTRADER_CLIENT_ID, CTRADER_CLIENT_SECRET, "
                "CTRADER_ACCESS_TOKEN, CTRADER_ACCOUNT_ID"
            )

        self.client: Optional[Client] = None
        self.connected = False
        self.positions: Dict[str, any] = {}
        self.on_tick_callback: Optional[Callable] = None

    def connect(self) -> bool:
        """
        Connect to cTrader API

        Returns:
            True if connected successfully
        """
        try:
            print(f"Connecting to cTrader at {self.host}:{self.port}...")

            # Create client
            self.client = Client(self.host, self.port, TcpProtocol)

            # Start the client
            self.client.start()

            # Authorize
            self._authorize()

            self.connected = True
            print("Connected to cTrader successfully!")
            return True

        except Exception as e:
            print(f"Failed to connect to cTrader: {e}")
            self.connected = False
            return False

    def _authorize(self):
        """Authorize with cTrader API"""
        request = ProtoOAApplicationAuthReq()
        request.clientId = self.client_id
        request.clientSecret = self.client_secret

        self.client.send(request)

        # Wait for auth response
        message = self.client.receive()
        if message.payloadType != ProtoOAApplicationAuthRes:
            raise Exception("Authorization failed")

        print("Authorized successfully")

    def disconnect(self):
        """Disconnect from cTrader API"""
        if self.client:
            self.client.stop()
            self.connected = False
            print("Disconnected from cTrader")

    def get_account_info(self) -> Dict:
        """
        Get account information

        Returns:
            Dictionary with account details
        """
        request = ProtoOATraderReq()
        request.ctidTraderAccountId = int(self.account_id)

        self.client.send(request)
        message = self.client.receive()

        if message.payloadType == ProtoOATraderRes:
            trader = message.trader
            return {
                'account_id': self.account_id,
                'balance': trader.balance / 100,  # Convert from cents
                'equity': trader.equity / 100 if hasattr(trader, 'equity') else None,
                'currency': trader.depositCurrency if hasattr(trader, 'depositCurrency') else 'USD'
            }
        else:
            raise Exception("Failed to get account info")

    def subscribe_to_spot_quotes(self, symbol_id: int):
        """
        Subscribe to real-time price quotes for a symbol

        Args:
            symbol_id: cTrader symbol ID
        """
        request = ProtoOASubscribeSpotsReq()
        request.ctidTraderAccountId = int(self.account_id)
        request.symbolId.append(symbol_id)

        self.client.send(request)
        print(f"Subscribed to quotes for symbol {symbol_id}")

    def get_symbol_id(self, symbol_name: str) -> Optional[int]:
        """
        Get symbol ID from symbol name (e.g., 'EURUSD')

        Args:
            symbol_name: Symbol name

        Returns:
            Symbol ID or None if not found
        """
        # Request symbols list
        request = ProtoOASymbolsListReq()
        request.ctidTraderAccountId = int(self.account_id)

        self.client.send(request)
        message = self.client.receive()

        if message.payloadType == ProtoOASymbolsListRes:
            for symbol in message.symbol:
                if symbol.symbolName == symbol_name:
                    return symbol.symbolId

        return None

    def open_market_order(
        self,
        symbol_id: int,
        volume: int,  # Volume in cents (10000 = 0.01 lots)
        side: str,  # "BUY" or "SELL"
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        label: Optional[str] = None
    ) -> Dict:
        """
        Open a market order

        Args:
            symbol_id: cTrader symbol ID
            volume: Order volume in cents (10000 = 0.01 lots)
            side: "BUY" or "SELL"
            stop_loss: Stop-loss price
            take_profit: Take-profit price
            label: Order label/comment

        Returns:
            Dictionary with order details
        """
        request = ProtoOANewOrderReq()
        request.ctidTraderAccountId = int(self.account_id)
        request.symbolId = symbol_id
        request.orderType = ProtoOAOrderType.MARKET
        request.tradeSide = ProtoOATradeSide.BUY if side == "BUY" else ProtoOATradeSide.SELL
        request.volume = volume

        if stop_loss:
            request.stopLoss = stop_loss
        if take_profit:
            request.takeProfit = take_profit
        if label:
            request.label = label

        self.client.send(request)
        message = self.client.receive()

        if message.payloadType == ProtoOAExecutionEvent:
            return {
                'order_id': message.order.orderId,
                'position_id': message.position.positionId if hasattr(message, 'position') else None,
                'executed': True
            }
        else:
            raise Exception("Failed to execute order")

    def close_position(self, position_id: int, volume: int) -> bool:
        """
        Close a position

        Args:
            position_id: Position ID to close
            volume: Volume to close

        Returns:
            True if closed successfully
        """
        request = ProtoOAClosePositionReq()
        request.ctidTraderAccountId = int(self.account_id)
        request.positionId = position_id
        request.volume = volume

        self.client.send(request)
        message = self.client.receive()

        return message.payloadType == ProtoOAExecutionEvent

    def modify_position(
        self,
        position_id: int,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None
    ) -> bool:
        """
        Modify position stop-loss and take-profit

        Args:
            position_id: Position ID
            stop_loss: New stop-loss price
            take_profit: New take-profit price

        Returns:
            True if modified successfully
        """
        request = ProtoOAAmendPositionSLTPReq()
        request.ctidTraderAccountId = int(self.account_id)
        request.positionId = position_id

        if stop_loss:
            request.stopLoss = stop_loss
        if take_profit:
            request.takeProfit = take_profit

        self.client.send(request)
        message = self.client.receive()

        return message.payloadType == ProtoOAExecutionEvent

    def get_open_positions(self) -> List[Dict]:
        """
        Get all open positions

        Returns:
            List of position dictionaries
        """
        # This would require processing execution events
        # For now, return cached positions
        return list(self.positions.values())

    def start_price_stream(self, symbol_name: str, callback: Callable):
        """
        Start streaming price data for a symbol

        Args:
            symbol_name: Symbol to stream (e.g., 'EURUSD')
            callback: Function to call with price updates
        """
        symbol_id = self.get_symbol_id(symbol_name)
        if symbol_id is None:
            raise ValueError(f"Symbol {symbol_name} not found")

        self.on_tick_callback = callback
        self.subscribe_to_spot_quotes(symbol_id)

        print(f"Started price stream for {symbol_name}")

    def lots_to_volume(self, lots: float) -> int:
        """
        Convert lots to cTrader volume (in cents)

        Args:
            lots: Lot size (e.g., 0.01)

        Returns:
            Volume in cents
        """
        # 1 lot = 100,000 units = 1,000,000 cents
        return int(lots * 1_000_000)

    def volume_to_lots(self, volume: int) -> float:
        """
        Convert cTrader volume to lots

        Args:
            volume: Volume in cents

        Returns:
            Lot size
        """
        return volume / 1_000_000


class LiveTrader:
    """
    Live trading integration with London Breakout Strategy

    This class connects the strategy to cTrader for live execution.
    """

    def __init__(self, symbol: str, client: CTraderClient):
        from strategy import LondonBreakoutStrategy
        from risk_management import RiskManager

        self.symbol = symbol
        self.client = client
        self.strategy = LondonBreakoutStrategy(symbol)

        # Get initial account balance
        account_info = client.get_account_info()
        initial_capital = account_info['balance']

        self.risk_manager = RiskManager(initial_capital)
        self.running = False

        print(f"Live Trader initialized for {symbol}")
        print(f"Account balance: ${initial_capital:,.2f}")

    def start(self):
        """Start live trading"""
        if not self.client.connected:
            raise Exception("Client not connected to cTrader")

        self.running = True
        print(f"Live trading started for {self.symbol}")

        # In production, you'd set up a main loop here
        # that processes incoming price data and generates signals

    def stop(self):
        """Stop live trading"""
        self.running = False
        print("Live trading stopped")

    def on_price_update(self, price_data: Dict):
        """
        Handle incoming price updates

        Args:
            price_data: Dictionary with OHLC data
        """
        # This is where you'd implement the live trading logic
        # 1. Update price data
        # 2. Check for signals
        # 3. Execute orders
        # 4. Monitor positions
        pass


# Example usage
def example_live_trading():
    """Example of how to use the cTrader API for live trading"""

    # Create client
    client = CTraderClient()

    try:
        # Connect to cTrader
        if not client.connect():
            print("Failed to connect")
            return

        # Get account info
        account = client.get_account_info()
        print(f"Account Balance: ${account['balance']:,.2f}")

        # Initialize live trader
        trader = LiveTrader("EURUSD", client)

        # Start trading (in practice, this would be a continuous loop)
        trader.start()

        # ... trading logic here ...

        # Stop trading
        trader.stop()

    except Exception as e:
        print(f"Error: {e}")

    finally:
        # Disconnect
        client.disconnect()


if __name__ == "__main__":
    if CTRADER_AVAILABLE:
        print("cTrader API module loaded successfully")
        print("To start live trading, configure your credentials and run example_live_trading()")
    else:
        print("Install OpenApiPy first:")
        print("pip install git+https://github.com/spotware/OpenApiPy.git")
