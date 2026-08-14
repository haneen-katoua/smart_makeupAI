import { useEffect, useState } from "react";
import api from "../../services/api";
import "../../styles/Users.css";


function Users() {


    const [users, setUsers] = useState([]);



    useEffect(() => {

        loadUsers();

    }, []);




    const loadUsers = async () => {

        try {

            const response = await api.get(
                "/api/accounts/admin/users/"
            );


            console.log(response.data);


            setUsers(
                response.data
            );


        } catch(error) {

            console.log(error);

        }

    };





    const handleDelete = async (id) => {


        const confirm =
            window.confirm(
                "Delete this user?"
            );


        if(!confirm)
            return;



        try {


            await api.delete(
                `api/accounts/admin/users/${id}/`
            );


            setUsers(
                users.filter(
                    user =>
                    user.id !== id
                )
            );


        } catch(error){

            console.log(error);

        }

    };




    return (

        <div className="users-page">


            <h1>
                Users Management
            </h1>



            <table className="users-table">


                <thead>

                    <tr>

                        <th>
                            ID
                        </th>


                        <th>
                            Username
                        </th>


                        <th>
                            Email
                        </th>


                        <th>
                            Action
                        </th>

                    </tr>

                </thead>



                <tbody>


                {
                    users.map(
                        user => (

                            <tr key={user.id}>


                                <td>
                                    {user.id}
                                </td>


                                <td>
                                    {user.username}
                                </td>


                                <td>
                                    {user.email}
                                </td>


                                <td>

                                    <button
                                        className="delete-btn"
                                        onClick={() =>
                                            handleDelete(
                                                user.id
                                            )
                                        }
                                    >
                                        Delete
                                    </button>

                                </td>


                            </tr>

                        )
                    )
                }


                </tbody>


            </table>


        </div>

    );

}


export default Users;