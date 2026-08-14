import axios from "axios";


const api = axios.create({
    baseURL: "http://127.0.0.1:8000",
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

    (response) => {

        return response;

    },

    async (error) => {

        const originalRequest =
            error.config;


        // إذا الخطأ ليس 401
        if (error.response?.status !== 401) {

            return Promise.reject(error);

        }


        // منع محاولة refresh لنفس الطلب أكثر من مرة
        if (originalRequest._retry) {

            return Promise.reject(error);

        }


        originalRequest._retry = true;


        const refreshToken =
            localStorage.getItem("refresh_token");


        // لا يوجد Refresh Token
        if (!refreshToken) {

            localStorage.removeItem("access_token");
            localStorage.removeItem("refresh_token");

            window.location.href =
                "/admin/login";

            return Promise.reject(error);

        }


        try {

            // طلب Access Token جديد
            const response = await axios.post(

                "http://127.0.0.1:8000/api/token/refresh/",

                {
                    refresh: refreshToken
                }

            );


            const newAccessToken =
                response.data.access;


            // حفظ التوكن الجديد
            localStorage.setItem(
                "access_token",
                newAccessToken
            );


            // تحديث Authorization للطلب الأصلي
            originalRequest.headers.Authorization =
                `Bearer ${newAccessToken}`;


            // إعادة تنفيذ الطلب الذي فشل
            return api(originalRequest);


        } catch (refreshError) {

            console.log(
                "Refresh token expired."
            );


            // انتهت جلسة الدخول بالكامل
            localStorage.removeItem(
                "access_token"
            );

            localStorage.removeItem(
                "refresh_token"
            );


            window.location.href =
                "/admin/login";


            return Promise.reject(
                refreshError
            );

        }

    }

);


export default api;