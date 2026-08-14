import { NavLink } from "react-router-dom";


function Sidebar(){

    return (

        <aside className="admin-sidebar">


            <NavLink to="/admin/dashboard">
                Dashboard
            </NavLink>


            <NavLink to="/admin/users">
                Users
            </NavLink>



            <NavLink to="/admin/analysis">
                Analysis
            </NavLink>



        </aside>

    );

}


export default Sidebar;