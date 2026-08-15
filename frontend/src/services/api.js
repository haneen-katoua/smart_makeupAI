import axios from "axios";


const API_BASE_URL = "http://127.0.0.1:8000";


const api = axios.create({

    baseURL: API_BASE_URL,

});



// =====================================================
// REQUEST INTERCEPTOR
// =====================================================

api.interceptors.request.use(

    (config) => {

        const accessToken =
            localStorage.getItem("access_token");


        if (accessToken) {

            config.headers.Authorization =
                `Bearer ${accessToken}`;

        }


        return config;

    },

    (error) => {

        return Promise.reject(error);

    }

);



// =====================================================
// RESPONSE INTERCEPTOR
// =====================================================

api.interceptors.response.use(

    // -----------------------------------------------
    // SUCCESS
    // -----------------------------------------------

    (response) => {

        return response;

    },


    // -----------------------------------------------
    // ERROR
    // -----------------------------------------------

    async (error) => {

        const originalRequest =
            error.config;


        // -------------------------------------------
        // إذا الخطأ ليس 401
        // -------------------------------------------

        if (
            error.response?.status !== 401
        ) {

            return Promise.reject(error);

        }


        // -------------------------------------------
        // منع Loop لا نهائي
        // -------------------------------------------

        if (
            originalRequest?._retry
        ) {

            return Promise.reject(error);

        }


        originalRequest._retry = true;



        // -------------------------------------------
        // Refresh Token
        // -------------------------------------------

        const refreshToken =
            localStorage.getItem(
                "refresh_token"
            );



        // -------------------------------------------
        // لا يوجد Refresh Token
        // -------------------------------------------

        if (!refreshToken) {

            localStorage.removeItem(
                "access_token"
            );

            localStorage.removeItem(
                "refresh_token"
            );


            redirectToLogin();


            return Promise.reject(error);

        }



        try {

            // ---------------------------------------
            // الحصول على Access Token جديد
            // ---------------------------------------

            const refreshResponse =
                await axios.post(

                    `${API_BASE_URL}/api/token/refresh/`,

                    {
                        refresh: refreshToken
                    }

                );


            const newAccessToken =
                refreshResponse.data.access;



            // ---------------------------------------
            // حفظ Access Token الجديد
            // ---------------------------------------

            localStorage.setItem(

                "access_token",

                newAccessToken

            );



            // ---------------------------------------
            // تحديث الطلب الأصلي
            // ---------------------------------------

            originalRequest.headers =
                originalRequest.headers || {};


            originalRequest.headers.Authorization =
                `Bearer ${newAccessToken}`;



            // ---------------------------------------
            // إعادة تنفيذ الطلب
            // ---------------------------------------

            return api(
                originalRequest
            );


        } catch (refreshError) {

            console.log(
                "Refresh token expired."
            );


            // ---------------------------------------
            // حذف Tokens
            // ---------------------------------------

            localStorage.removeItem(
                "access_token"
            );

            localStorage.removeItem(
                "refresh_token"
            );


            redirectToLogin();


            return Promise.reject(
                refreshError
            );

        }

    }

);



// =====================================================
// LOGIN REDIRECT
// =====================================================

function redirectToLogin() {

    const currentPath =
        window.location.pathname;


    // -----------------------------------------------
    // ADMIN
    // -----------------------------------------------

    if (
        currentPath.startsWith("/admin")
    ) {

        window.location.href =
            "/admin/login";

        return;

    }


    // -----------------------------------------------
    // USER
    // -----------------------------------------------

    window.location.href =
        "/login";

}

import { Client } from "@gradio/client";

export const applySmartMakeup = async (imageFile) => {
  try {
    const app = await Client.connect("http://localhost:7860/");

    const result = await app.predict("/handle_apply", [ imageFile ]);

    return {
      success: true,
      beforeImage: result.data[0]?.url,
      afterImage: result.data[1]?.url,
      statusMessage: result.data[2],
      recommendationsHtml: result.data[5]
    };
  } catch (error) {
    console.error("Gradio Integration Error:", error);
    return { success: false, error: error.message };
  }
};

// =====================================================
// EXPORT
// =====================================================

export default api;