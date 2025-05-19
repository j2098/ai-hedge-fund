import React, { useState, useEffect } from "react";
import { Button } from "./button";
import { Input } from "./input";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "./card";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "./dialog";
import { Badge } from "./badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./tabs";
import { Separator } from "./separator";

// 定义Moomoo连接设置类型
interface MoomooConnectionSettings {
  host: string;
  port: number;
  api_key?: string;
  trade_env: "SIMULATE" | "REAL";
}

// 定义Moomoo连接状态类型
interface MoomooConnectionStatus {
  connected: boolean;
  message: string;
}

// 定义Moomoo持仓类型
interface MoomooPosition {
  ticker: string;
  quantity: number;
  cost_price: number;
  current_price: number;
  market_value: number;
  profit_loss: number;
  profit_loss_ratio: number;
  today_profit_loss: number;
  position_ratio: number;
}

// 定义Moomoo账户信息类型
interface MoomooAccountInfo {
  power: number;
  total_assets: number;
  cash: number;
  market_value: number;
  frozen_cash: number;
  available_cash: number;
}

// 定义Moomoo持仓响应类型
interface MoomooPositionsResponse {
  positions: Record<string, MoomooPosition>;
  account_info: MoomooAccountInfo;
}

// Moomoo连接组件
export function MoomooConnect() {
  // 状态
  const [isOpen, setIsOpen] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<MoomooConnectionStatus>({ connected: false, message: "Not connected" });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [importSuccess, setImportSuccess] = useState<string | null>(null);
  const [settings, setSettings] = useState<MoomooConnectionSettings>({
    host: "127.0.0.1",
    port: 11111,
    api_key: "",
    trade_env: "SIMULATE",
  });
  const [positions, setPositions] = useState<Record<string, MoomooPosition>>({});
  const [accountInfo, setAccountInfo] = useState<MoomooAccountInfo | null>(null);
  const [activeTab, setActiveTab] = useState("connect");

  // 获取连接状态
  const fetchConnectionStatus = async () => {
    try {
      const response = await fetch("/api/moomoo/status");
      const data = await response.json();
      setConnectionStatus(data);

      if (data.connected) {
        fetchPositions();
      }
    } catch (err) {
      console.error("Error fetching connection status:", err);
    }
  };

  // 获取持仓信息
  const fetchPositions = async () => {
    try {
      setIsLoading(true);
      const response = await fetch("/api/moomoo/positions");

      if (!response.ok) {
        throw new Error(`Failed to fetch positions: ${response.statusText}`);
      }

      const data: MoomooPositionsResponse = await response.json();
      setPositions(data.positions);
      setAccountInfo(data.account_info);
      setActiveTab("positions");
    } catch (err) {
      console.error("Error fetching positions:", err);
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setIsLoading(false);
    }
  };

  // 连接到Moomoo
  const connectToMoomoo = async () => {
    try {
      setIsLoading(true);
      setError(null);

      const response = await fetch("/api/moomoo/connect", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(settings),
      });

      if (!response.ok) {
        const errorData = await response.json();
        console.error("Error response:", errorData);
        throw new Error(errorData.detail || "Failed to connect to Moomoo");
      }

      const data = await response.json();
      setConnectionStatus(data);

      if (data.connected) {
        fetchPositions();
      }
    } catch (err) {
      console.error("Error connecting to Moomoo:", err);
      if (err instanceof Error) {
        setError(err.message);
      } else if (typeof err === 'object' && err !== null) {
        setError(JSON.stringify(err));
      } else {
        setError("Unknown error");
      }
    } finally {
      setIsLoading(false);
    }
  };

  // 断开与Moomoo的连接
  const disconnectFromMoomoo = async () => {
    try {
      setIsLoading(true);

      const response = await fetch("/api/moomoo/disconnect", {
        method: "POST",
      });

      if (!response.ok) {
        throw new Error("Failed to disconnect from Moomoo");
      }

      const data = await response.json();
      setConnectionStatus(data);
      setPositions({});
      setAccountInfo(null);
      setActiveTab("connect");
    } catch (err) {
      console.error("Error disconnecting from Moomoo:", err);
    } finally {
      setIsLoading(false);
    }
  };

  // 导入投资组合
  const importPortfolio = async () => {
    try {
      setIsLoading(true);
      setError(null);
      setImportSuccess(null);

      const response = await fetch("/api/moomoo/portfolio/import", {
        method: "POST",
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to import portfolio");
      }

      const data = await response.json();
      if (data.success) {
        setImportSuccess(data.message);
        // 显示成功消息5秒后清除
        setTimeout(() => setImportSuccess(null), 5000);
      } else {
        setError(data.message);
      }
    } catch (err) {
      console.error("Error importing portfolio:", err);
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setIsLoading(false);
    }
  };

  // 处理设置变更
  const handleSettingsChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setSettings((prev) => ({
      ...prev,
      [name]: name === "port" ? parseInt(value) : value,
    }));
  };

  // 初始化时获取连接状态
  useEffect(() => {
    fetchConnectionStatus();
  }, []);

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" className="flex items-center gap-2">
          <span className={`w-2 h-2 rounded-full ${connectionStatus.connected ? "bg-green-500" : "bg-red-500"}`} />
          Moomoo
          {connectionStatus.connected && <Badge variant="outline">Connected</Badge>}
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle>Moomoo Trading Account</DialogTitle>
          <DialogDescription>
            Connect to your Moomoo trading account to import your portfolio.
          </DialogDescription>
        </DialogHeader>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="connect">Connection</TabsTrigger>
            <TabsTrigger value="positions" disabled={!connectionStatus.connected}>
              Portfolio
            </TabsTrigger>
          </TabsList>

          <TabsContent value="connect" className="space-y-4 py-4">
            <div className="flex items-center justify-between">
              <div>
                <h4 className="text-sm font-medium">Connection Status</h4>
                <p className="text-sm text-muted-foreground">{connectionStatus.message}</p>
              </div>
              <Badge variant={connectionStatus.connected ? "success" : "destructive"}>
                {connectionStatus.connected ? "Connected" : "Disconnected"}
              </Badge>
            </div>

            <Separator />

            {!connectionStatus.connected && (
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label htmlFor="host" className="text-sm font-medium">Host</label>
                    <Input
                      id="host"
                      name="host"
                      value={settings.host}
                      onChange={handleSettingsChange}
                      placeholder="127.0.0.1"
                    />
                  </div>
                  <div className="space-y-2">
                    <label htmlFor="port" className="text-sm font-medium">Port</label>
                    <Input
                      id="port"
                      name="port"
                      type="number"
                      value={settings.port}
                      onChange={handleSettingsChange}
                      placeholder="11111"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <label htmlFor="api_key" className="text-sm font-medium">API Key (Optional)</label>
                  <Input
                    id="api_key"
                    name="api_key"
                    type="password"
                    value={settings.api_key}
                    onChange={handleSettingsChange}
                    placeholder="Enter your API key (optional)"
                  />
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">Trading Environment</label>
                  <div className="flex space-x-4">
                    <label className="flex items-center space-x-2">
                      <input
                        type="radio"
                        name="trade_env"
                        value="SIMULATE"
                        checked={settings.trade_env === "SIMULATE"}
                        onChange={handleSettingsChange}
                      />
                      <span>Simulation</span>
                    </label>
                    <label className="flex items-center space-x-2">
                      <input
                        type="radio"
                        name="trade_env"
                        value="REAL"
                        checked={settings.trade_env === "REAL"}
                        onChange={handleSettingsChange}
                      />
                      <span>Real Trading</span>
                    </label>
                  </div>
                </div>

                {error && (
                  <div className="text-sm text-red-500 p-2 bg-red-50 rounded">
                    {error}
                  </div>
                )}

                {importSuccess && (
                  <div className="text-sm text-green-500 p-2 bg-green-50 rounded">
                    {importSuccess}
                  </div>
                )}
              </div>
            )}
          </TabsContent>

          <TabsContent value="positions" className="space-y-4 py-4">
            {isLoading ? (
              <div className="text-center py-4">Loading portfolio data...</div>
            ) : (
              <>
                {accountInfo && (
                  <Card>
                    <CardHeader>
                      <CardTitle>Account Summary</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-3 gap-4">
                        <div>
                          <p className="text-sm text-muted-foreground">Total Assets</p>
                          <p className="text-lg font-medium">${accountInfo.total_assets.toLocaleString()}</p>
                        </div>
                        <div>
                          <p className="text-sm text-muted-foreground">Cash</p>
                          <p className="text-lg font-medium">${accountInfo.cash.toLocaleString()}</p>
                        </div>
                        <div>
                          <p className="text-sm text-muted-foreground">Market Value</p>
                          <p className="text-lg font-medium">${accountInfo.market_value.toLocaleString()}</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                )}

                <Card>
                  <CardHeader>
                    <CardTitle>Portfolio Holdings</CardTitle>
                    <CardDescription>
                      {Object.keys(positions).length} stocks in your portfolio
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    {Object.keys(positions).length > 0 ? (
                      <div className="space-y-4">
                        {Object.entries(positions).map(([ticker, position]) => (
                          <div key={ticker} className="flex justify-between items-center p-2 border rounded">
                            <div>
                              <p className="font-medium">{ticker}</p>
                              <p className="text-sm text-muted-foreground">{position.quantity} shares</p>
                            </div>
                            <div className="text-right">
                              <p className="font-medium">${position.market_value.toLocaleString()}</p>
                              <p className={`text-sm ${position.profit_loss >= 0 ? "text-green-600" : "text-red-600"}`}>
                                {position.profit_loss >= 0 ? "+" : ""}{position.profit_loss.toLocaleString()} ({(position.profit_loss_ratio * 100).toFixed(2)}%)
                              </p>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="text-center py-4 text-muted-foreground">
                        No positions found in your portfolio
                      </div>
                    )}
                  </CardContent>
                </Card>
              </>
            )}
          </TabsContent>
        </Tabs>

        <DialogFooter>
          {connectionStatus.connected ? (
            <>
              <Button variant="outline" onClick={() => fetchPositions()} disabled={isLoading}>
                Refresh Data
              </Button>
              <Button variant="default" onClick={importPortfolio} disabled={isLoading}>
                Import Portfolio
              </Button>
              <Button variant="destructive" onClick={disconnectFromMoomoo} disabled={isLoading}>
                Disconnect
              </Button>
            </>
          ) : (
            <Button onClick={connectToMoomoo} disabled={isLoading}>
              {isLoading ? "Connecting..." : "Connect to Moomoo"}
            </Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
