import { useEffect, useState } from "react";
import api from "../../services/api";
import "../../styles/AdminDashboard.css";


function AdminDashboard() {


    const [stats, setStats] = useState({
        total_users: 0,
        total_analyses: 0,
        today_analyses: 0
    });


    const [occasions, setOccasions] = useState({});


    const [recent, setRecent] = useState([]);



    useEffect(() => {

        fetchDashboard();

    }, []);




    const fetchDashboard = async () => {

        try {


            const statsResponse =
                await api.get(
                    "/api/analysis/admin/dashboard/"
                );


            setStats(
                statsResponse.data
            );



            const occasionResponse =
                await api.get(
                    "/api/analysis/admin/dashboard/occasions/"
                );


            setOccasions(
                occasionResponse.data
            );



            const recentResponse =
                await api.get(
                    "/api/analysis/admin/dashboard/recent/"
                );


            setRecent(
                recentResponse.data
            );



        } catch(error) {

            console.log(error);

        }

    };




    return (

        <div className="dashboard-page">


            {/* Navbar */}

            <nav className="dashboard-navbar">

                <h2>
                    Smart Makeup AI
                </h2>


                <span>
                    Admin Dashboard
                </span>


            </nav>




            <main className="dashboard-content">



                {/* Cards */}


                <div className="stats-container">


                    <div className="stat-card">

                        <h3>
                            Total Users
                        </h3>

                        <p>
                            {stats.total_users}
                        </p>

                    </div>




                    <div className="stat-card">

                        <h3>
                            Total Analyses
                        </h3>

                        <p>
                            {stats.total_analyses}
                        </p>

                    </div>




                    <div className="stat-card">

                        <h3>
                            Today Analyses
                        </h3>

                        <p>
                            {stats.today_analyses}
                        </p>

                    </div>


                </div>






                {/* Occasions */}


                <section className="dashboard-box">


                    <h2>
                        Analyses By Occasion
                    </h2>



                    {
                        Object.keys(occasions)
                        .map((key)=>(


                            <div
                                className="occasion-row"
                                key={key}
                            >

                                <span>
                                    {key}
                                </span>


                                <strong>
                                    {occasions[key]}
                                </strong>


                            </div>


                        ))
                    }



                </section>







                {/* Recent */}



                <section className="dashboard-box">


                    <h2>
                        Recent Analyses
                    </h2>



                    <table>


                        <thead>

                            <tr>

                                <th>
                                    User
                                </th>

                                <th>
                                    Occasion
                                </th>

                                <th>
                                    Date
                                </th>


                            </tr>

                        </thead>



                        <tbody>


                            {
                                recent.map(
                                    (item)=>(

                                    <tr key={item.id}>

                                        <td>
                                            {item.username}
                                        </td>


                                        <td>
                                            {item.occasion}
                                        </td>


                                        <td>
                                            {
                                                new Date(
                                                    item.created_at
                                                )
                                                .toLocaleDateString()
                                            }
                                        </td>


                                    </tr>

                                    )
                                )
                            }


                        </tbody>


                    </table>



                </section>



            </main>


        </div>

    );

}


export default AdminDashboard;