import { BrowserRouter, Route, Routes } from "react-router-dom";
import './App.css'
import './app1/styles/globals.css'
import HomePage from "./app1/pages/page";
import LoginPage from "./app1/pages/login/page";
import RegisterPage from "./app1/pages/register/page";
import DashboardPage from "./app1/pages/dashboard/page";
import FarmsPage from "./app1/pages/farms/page";
import FlocksPage from "./app1/pages/flocks/page";
import HealthPage from "./app1/pages/health/page";
import ProductionPage from "./app1/pages/production/page";
import ReportsPage from "./app1/pages/reports/page";
import SettingsPage from "./app1/pages/settings/page";


/**
 * The main App component, which wraps the entire application in a BrowserRouter
 * and defines the routes for the different pages.
 */
function App() {

  return (
    <div className="min-h-screen">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<HomePage/>}/>
          <Route path="/login" element={<LoginPage/>}/>
          <Route path="/register" element={<RegisterPage/>}/>
          <Route path="/dashboard" element={<DashboardPage/>}/>
          <Route path="/farms" element={<FarmsPage/>}/>
          <Route path="/flocks" element={<FlocksPage/>}/>
          <Route path="/health" element={<HealthPage/>}/>
          <Route path="/production" element={<ProductionPage/>}/>
          <Route path="/reports" element={<ReportsPage/>}/>
          <Route path="/settings" element={<SettingsPage/>}/>
        </Routes>
      </BrowserRouter>
    </div>
  )
}

export default App
