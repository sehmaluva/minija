import { BrowserRouter, Route, Routes } from "react-router-dom";
import './App.css'
import './app1/styles/globals.css'
import HomePage from "./app1/pages/page";
import LoginPage from "./app1/pages/login/page";
import RegisterPage from "./app1/pages/register/page";
import DashboardPage from "./app1/pages/dashboard/page";
import OrdersPage from "./app1/pages/orders/page";
import AccountingPage from "./app1/pages/accounting/page";
import ForecastPage from "./app1/pages/forecast/page";
import ReportsPage from "./app1/pages/reports/page";
import SettingsPage from "./app1/pages/settings/page";
import Layout from "./app1/components/Layout";


/**
 * The main App component, which wraps the entire application in a BrowserRouter
 * and defines the routes for the different pages.
 */
function App() {

  return (
    <div className="min-h-screen">
      <BrowserRouter>
        <Layout>
          <Routes>
            <Route path="/" element={<HomePage/>}/>
            <Route path="/login" element={<LoginPage/>}/>
            <Route path="/register" element={<RegisterPage/>}/>
            <Route path="/dashboard" element={<DashboardPage/>}/>
            <Route path="/orders" element={<OrdersPage/>}/>
            <Route path="/accounting" element={<AccountingPage/>}/>
            <Route path="/forecast" element={<ForecastPage/>}/>
            <Route path="/reports" element={<ReportsPage/>}/>
            <Route path="/settings" element={<SettingsPage/>}/>
          </Routes>
        </Layout>
      </BrowserRouter>
    </div>
  )
}

export default App
