import { BrowserRouter, Routes, Route } from "react-router-dom";

// ================= USER =================

import UserLogin from "../user/UserLogin";
import UserRegister from "../user/UserRegister";
import MakeupRequest from "../user/MakeupRequest";
import MakeupSteps from "../user/MakeupSteps";
import UserProfile from "../user/UserProfile";
import UserAnalysisDetails from "../user/UserAnalysisDetails";


// ================= ADMIN =================

import AdminLogin from "../pages/admin/AdminLogin";
import AdminDashboard from "../pages/admin/AdminDashboard";
import AdminLayout from "../layouts/AdminLayout";
import Users from "../pages/admin/Users";
import Analysis from "../pages/admin/Analysis";
import AnalysisDetails from "../pages/admin/AnalysisDetails";


function AppRoutes() {

    return (

        <BrowserRouter>

            <Routes>


                {/* ================================================== */}
                {/* USER */}
                {/* ================================================== */}

                <Route
                    path="/login"
                    element={<UserLogin />}
                />

                <Route
                    path="/register"
                    element={<UserRegister />}
                />
                <Route
                    path="/makeup-request"
                    element={<MakeupRequest />}
                />

                <Route
                path="/profile"
                element={<UserProfile />}
            />
            <Route
                path="/my-analyses/:id"
                element={<UserAnalysisDetails />}
            />

                <Route
                path="/makeup-steps/:id"
                element={<MakeupSteps />}
            />


                {/* ================================================== */}
                {/* ADMIN LOGIN */}
                {/* ================================================== */}

                <Route
                    path="/admin/login"
                    element={<AdminLogin />}
                />


                {/* ================================================== */}
                {/* ADMIN LAYOUT */}
                {/* ================================================== */}

                <Route
                    path="/admin"
                    element={<AdminLayout />}
                >


                    {/* ================= DASHBOARD ================= */}

                    <Route
                        path="dashboard"
                        element={<AdminDashboard />}
                    />


                    {/* ================= USERS ================= */}

                    <Route
                        path="users"
                        element={<Users />}
                    />


                    {/* ================= ANALYSIS ================= */}

                    <Route
                        path="analysis"
                        element={<Analysis />}
                    />


                    {/* ============== ANALYSIS DETAILS ============== */}

                    <Route
                        path="analysis/:id"
                        element={<AnalysisDetails />}
                    />


                </Route>


                {/* ================================================== */}
                {/* DEFAULT */}
                {/* ================================================== */}

                <Route
                    path="/"
                    element={<UserLogin />}
                />


            </Routes>

        </BrowserRouter>

    );

}


export default AppRoutes;