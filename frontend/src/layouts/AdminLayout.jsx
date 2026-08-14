import { Outlet } from "react-router-dom";

import Navbar from "../components/admin/Navbar";
import Sidebar from "../components/admin/Sidebar";

import "../styles/Navbar.css";
import "../styles/Sidebar.css";
import "../styles/AdminLayout.css";


function AdminLayout(){


    return (

        <>

            <Navbar />

            <Sidebar />


            <main className="admin-content">

                <Outlet />

            </main>


        </>

    );

}


export default AdminLayout;