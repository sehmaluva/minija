import { BrowserRouter, Route, Routes } from "react-router-dom";
import Page from "./app1/app/login/page";
// import Page from "./app1/app/dashboard/page";


function App() {

  return (
    <div> 
      <BrowserRouter>
        <Routes>
        <Route path="/" element={<Page/>}/>

        </Routes>
      </BrowserRouter>
    </div>
  )
}

export default App
