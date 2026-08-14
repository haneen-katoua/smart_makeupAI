import {
    BrowserRouter,
    Routes,
    Route
} from "react-router-dom";


import AdminLogin from "../pages/admin/AdminLogin";
import AdminLayout from "../layouts/AdminLayout";
import AdminDashboard from "../pages/admin/AdminDashboard";
import Users from "../pages/admin/Users";
import AnalysisDetails from "../pages/admin/AnalysisDetails";
import Analysis from "../pages/admin/Analysis";




function AppRoutes(){


    return (

        <BrowserRouter>

            <Routes>


                <Route
                    path="/admin/login"
                    element={
                        <AdminLogin />
                    }
                />



                <Route
                    path="/admin"
                    element={
                        <AdminLayout />
                    }
                >


                    <Route
                        path="dashboard"
                        element={
                            <AdminDashboard />
                        }
                    />

                    <Route
                    path="users"
                    element={
                        <Users />
                    }
                />

                                <Route
                    path="analysis"
                    element={
                        <Analysis />
                    }
                />


                <Route
                    path="analysis/:id"
                    element={
                        <AnalysisDetails />
                    }
                />


                </Route>


            </Routes>

        </BrowserRouter>

    );

}


export default AppRoutes;