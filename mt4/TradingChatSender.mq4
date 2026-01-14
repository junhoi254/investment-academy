//+------------------------------------------------------------------+
//|                                              TradingChatSender.mq4 |
//|                                         Trading Chat System      |
//|                                                                  |
//+------------------------------------------------------------------+
#property copyright "Trading Chat System"
#property link      "https://your-api-url.com"
#property version   "1.00"
#property strict

// 입력 파라미터
input string API_URL = "http://your-server-url.com/api/mt4/position"; // API URL
input string API_KEY = "your-mt4-api-key"; // API 키
input bool EnableNotification = true; // 알림 활성화

// 전역 변수
int lastTicket = -1;
datetime lastOrderTime = 0;

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
{
   Print("Trading Chat Sender EA 시작");
   return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   Print("Trading Chat Sender EA 종료");
}

//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
{
   // 새로운 포지션 확인
   CheckNewPositions();
}

//+------------------------------------------------------------------+
//| 새로운 포지션 확인                                               |
//+------------------------------------------------------------------+
void CheckNewPositions()
{
   for(int i = OrdersTotal() - 1; i >= 0; i--)
   {
      if(OrderSelect(i, SELECT_BY_POS, MODE_TRADES))
      {
         // 현재 심볼의 주문만 처리
         if(OrderSymbol() == Symbol())
         {
            // 새로운 주문인지 확인
            if(OrderTicket() != lastTicket && OrderOpenTime() > lastOrderTime)
            {
               // 포지션 정보 전송
               SendPositionToAPI(OrderTicket());
               
               lastTicket = OrderTicket();
               lastOrderTime = OrderOpenTime();
            }
         }
      }
   }
}

//+------------------------------------------------------------------+
//| API로 포지션 정보 전송                                           |
//+------------------------------------------------------------------+
void SendPositionToAPI(int ticket)
{
   if(!OrderSelect(ticket, SELECT_BY_TICKET))
   {
      Print("주문 선택 실패: ", ticket);
      return;
   }
   
   // JSON 데이터 생성
   string jsonData = "{";
   jsonData += "\"symbol\": \"" + OrderSymbol() + "\",";
   jsonData += "\"type\": \"" + (OrderType() == OP_BUY ? "BUY" : "SELL") + "\",";
   jsonData += "\"lots\": " + DoubleToString(OrderLots(), 2) + ",";
   jsonData += "\"open_price\": " + DoubleToString(OrderOpenPrice(), 5) + ",";
   jsonData += "\"sl\": " + DoubleToString(OrderStopLoss(), 5) + ",";
   jsonData += "\"tp\": " + DoubleToString(OrderTakeProfit(), 5) + ",";
   jsonData += "\"open_time\": \"" + TimeToString(OrderOpenTime(), TIME_DATE|TIME_SECONDS) + "\"";
   jsonData += "}";
   
   // HTTP 요청
   string headers = "Content-Type: application/json\r\n";
   headers += "X-API-Key: " + API_KEY + "\r\n";
   
   char post[];
   char result[];
   string resultHeaders;
   
   StringToCharArray(jsonData, post, 0, StringLen(jsonData));
   
   int res = WebRequest("POST", 
                        API_URL, 
                        headers, 
                        5000, 
                        post, 
                        result, 
                        resultHeaders);
   
   if(res == 200)
   {
      Print("✅ 포지션 전송 성공: ", OrderSymbol(), " ", 
            (OrderType() == OP_BUY ? "BUY" : "SELL"), " ", 
            DoubleToString(OrderLots(), 2));
            
      if(EnableNotification)
      {
         SendNotification("새 포지션: " + OrderSymbol() + " " + 
                         (OrderType() == OP_BUY ? "매수" : "매도") + " " + 
                         DoubleToString(OrderLots(), 2));
      }
   }
   else
   {
      Print("❌ 포지션 전송 실패. 오류 코드: ", res);
      Print("응답: ", CharArrayToString(result));
   }
}

//+------------------------------------------------------------------+
//| 주문 이벤트                                                      |
//+------------------------------------------------------------------+
void OnTradeTransaction(const MqlTradeTransaction& trans,
                       const MqlTradeRequest& request,
                       const MqlTradeResult& result)
{
   // MT5용 - 트레이드 트랜잭션 처리
   if(trans.type == TRADE_TRANSACTION_DEAL_ADD)
   {
      // 새로운 거래 발생
      Print("새 거래 감지");
   }
}
//+------------------------------------------------------------------+
