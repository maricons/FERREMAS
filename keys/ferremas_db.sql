--
-- PostgreSQL database dump
--

-- Dumped from database version 16.9 (Ubuntu 16.9-0ubuntu0.24.04.1)
-- Dumped by pg_dump version 16.9 (Ubuntu 16.9-0ubuntu0.24.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: public; Type: SCHEMA; Schema: -; Owner: ferremas
--

-- *not* creating schema, since initdb creates it


ALTER SCHEMA public OWNER TO ferremas;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: ferremas
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO ferremas;

--
-- Name: cart_items; Type: TABLE; Schema: public; Owner: ferremas
--

CREATE TABLE public.cart_items (
    id integer NOT NULL,
    user_id integer NOT NULL,
    product_id integer NOT NULL,
    quantity integer NOT NULL
);


ALTER TABLE public.cart_items OWNER TO ferremas;

--
-- Name: cart_items_id_seq; Type: SEQUENCE; Schema: public; Owner: ferremas
--

CREATE SEQUENCE public.cart_items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.cart_items_id_seq OWNER TO ferremas;

--
-- Name: cart_items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ferremas
--

ALTER SEQUENCE public.cart_items_id_seq OWNED BY public.cart_items.id;


--
-- Name: categories; Type: TABLE; Schema: public; Owner: ferremas
--

CREATE TABLE public.categories (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    description character varying(200),
    icon character varying(50),
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.categories OWNER TO ferremas;

--
-- Name: categories_id_seq; Type: SEQUENCE; Schema: public; Owner: ferremas
--

CREATE SEQUENCE public.categories_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.categories_id_seq OWNER TO ferremas;

--
-- Name: categories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ferremas
--

ALTER SEQUENCE public.categories_id_seq OWNED BY public.categories.id;


--
-- Name: order_items; Type: TABLE; Schema: public; Owner: ferremas
--

CREATE TABLE public.order_items (
    id integer NOT NULL,
    order_id integer NOT NULL,
    product_id integer,
    quantity integer NOT NULL,
    price_at_time numeric(10,2) NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.order_items OWNER TO ferremas;

--
-- Name: order_items_id_seq; Type: SEQUENCE; Schema: public; Owner: ferremas
--

CREATE SEQUENCE public.order_items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.order_items_id_seq OWNER TO ferremas;

--
-- Name: order_items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ferremas
--

ALTER SEQUENCE public.order_items_id_seq OWNED BY public.order_items.id;


--
-- Name: orders; Type: TABLE; Schema: public; Owner: ferremas
--

CREATE TABLE public.orders (
    id integer NOT NULL,
    user_id integer,
    total_amount numeric(10,2) NOT NULL,
    status character varying(20) NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.orders OWNER TO ferremas;

--
-- Name: orders_id_seq; Type: SEQUENCE; Schema: public; Owner: ferremas
--

CREATE SEQUENCE public.orders_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.orders_id_seq OWNER TO ferremas;

--
-- Name: orders_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ferremas
--

ALTER SEQUENCE public.orders_id_seq OWNED BY public.orders.id;


--
-- Name: products; Type: TABLE; Schema: public; Owner: ferremas
--

CREATE TABLE public.products (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    price double precision NOT NULL,
    image character varying(200),
    description text,
    stock integer,
    is_featured boolean,
    is_promotion boolean,
    promotion_price double precision,
    category_id integer,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.products OWNER TO ferremas;

--
-- Name: products_id_seq; Type: SEQUENCE; Schema: public; Owner: ferremas
--

CREATE SEQUENCE public.products_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.products_id_seq OWNER TO ferremas;

--
-- Name: products_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ferremas
--

ALTER SEQUENCE public.products_id_seq OWNED BY public.products.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: ferremas
--

CREATE TABLE public.users (
    id integer NOT NULL,
    username character varying(80) NOT NULL,
    password character varying(200) NOT NULL,
    email character varying(120) NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    is_active boolean,
    is_admin boolean
);


ALTER TABLE public.users OWNER TO ferremas;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: ferremas
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO ferremas;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ferremas
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: webpay_transactions; Type: TABLE; Schema: public; Owner: ferremas
--

CREATE TABLE public.webpay_transactions (
    id integer NOT NULL,
    order_id integer,
    buy_order character varying(50) NOT NULL,
    token_ws character varying(100),
    amount numeric(10,2) NOT NULL,
    status character varying(20) NOT NULL,
    transaction_date timestamp with time zone,
    authorization_code character varying(20),
    payment_type_code character varying(20),
    response_code character varying(10),
    installments_number integer,
    card_number character varying(20),
    transaction_detail text,
    session_id character varying(100),
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.webpay_transactions OWNER TO ferremas;

--
-- Name: webpay_transactions_id_seq; Type: SEQUENCE; Schema: public; Owner: ferremas
--

CREATE SEQUENCE public.webpay_transactions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.webpay_transactions_id_seq OWNER TO ferremas;

--
-- Name: webpay_transactions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ferremas
--

ALTER SEQUENCE public.webpay_transactions_id_seq OWNED BY public.webpay_transactions.id;


--
-- Name: cart_items id; Type: DEFAULT; Schema: public; Owner: ferremas
--

ALTER TABLE ONLY public.cart_items ALTER COLUMN id SET DEFAULT nextval('public.cart_items_id_seq'::regclass);


--
-- Name: categories id; Type: DEFAULT; Schema: public; Owner: ferremas
--

ALTER TABLE ONLY public.categories ALTER COLUMN id SET DEFAULT nextval('public.categories_id_seq'::regclass);


--
-- Name: order_items id; Type: DEFAULT; Schema: public; Owner: ferremas
--

ALTER TABLE ONLY public.order_items ALTER COLUMN id SET DEFAULT nextval('public.order_items_id_seq'::regclass);


--
-- Name: orders id; Type: DEFAULT; Schema: public; Owner: ferremas
--

ALTER TABLE ONLY public.orders ALTER COLUMN id SET DEFAULT nextval('public.orders_id_seq'::regclass);


--
-- Name: products id; Type: DEFAULT; Schema: public; Owner: ferremas
--

ALTER TABLE ONLY public.products ALTER COLUMN id SET DEFAULT nextval('public.products_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: ferremas
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Name: webpay_transactions id; Type: DEFAULT; Schema: public; Owner: ferremas
--

ALTER TABLE ONLY public.webpay_transactions ALTER COLUMN id SET DEFAULT nextval('public.webpay_transactions_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: ferremas
--

COPY public.alembic_version (version_num) FROM stdin;
e3054377f32b
\.


--
-- Data for Name: cart_items; Type: TABLE DATA; Schema: public; Owner: ferremas
--

COPY public.cart_items (id, user_id, product_id, quantity) FROM stdin;
3	1	9	1
4	1	18	2
\.


--
-- Data for Name: categories; Type: TABLE DATA; Schema: public; Owner: ferremas
--

COPY public.categories (id, name, description, icon, created_at) FROM stdin;
1	Herramientas Manuales	Herramientas básicas para el hogar y trabajo profesional	fas fa-tools	2025-05-22 08:29:37.340687+00
2	Herramientas Eléctricas	Taladros, sierras y otras herramientas eléctricas	fas fa-bolt	2025-05-22 08:29:37.340687+00
3	Materiales de Construcción	Cemento, ladrillos, arena y otros materiales	fas fa-hard-hat	2025-05-22 08:29:37.340687+00
4	Pinturas y Acabados	Pinturas, barnices y productos para acabados	fas fa-paint-roller	2025-05-22 08:29:37.340687+00
5	Plomería	Tuberías, grifería y accesorios de plomería	fas fa-faucet	2025-05-22 08:29:37.340687+00
6	Electricidad	Cables, interruptores y accesorios eléctricos	fas fa-plug	2025-05-22 08:29:37.340687+00
7	Seguridad	Equipos de protección personal y seguridad	fas fa-shield-alt	2025-05-22 08:29:37.340687+00
8	Jardín	Herramientas y accesorios para jardín	fas fa-leaf	2025-05-22 08:29:37.340687+00
\.


--
-- Data for Name: order_items; Type: TABLE DATA; Schema: public; Owner: ferremas
--

COPY public.order_items (id, order_id, product_id, quantity, price_at_time, created_at) FROM stdin;
1	1	7	1	15990.00	2025-05-22 08:40:09.385263+00
2	2	9	1	89990.00	2025-05-22 08:40:51.019511+00
\.


--
-- Data for Name: orders; Type: TABLE DATA; Schema: public; Owner: ferremas
--

COPY public.orders (id, user_id, total_amount, status, created_at, updated_at) FROM stdin;
1	1	15990.00	pending	2025-05-22 08:40:09.385263+00	2025-05-22 08:40:09.385263+00
2	1	89990.00	completed	2025-05-22 08:40:51.019511+00	2025-05-22 08:41:25.184482+00
\.


--
-- Data for Name: products; Type: TABLE DATA; Schema: public; Owner: ferremas
--

COPY public.products (id, name, price, image, description, stock, is_featured, is_promotion, promotion_price, category_id, created_at, updated_at) FROM stdin;
7	Martillo Profesional	15990	martillo.jpg	Martillo de acero forjado con mango ergonómico	50	t	f	\N	1	2025-05-22 08:29:46.798962+00	2025-05-22 08:29:46.798962+00
8	Set de Destornilladores	24990	destornilladores.jpg	Set de 6 destornilladores con puntas intercambiables	30	t	f	\N	1	2025-05-22 08:29:46.798962+00	2025-05-22 08:29:46.798962+00
9	Taladro Inalámbrico	89990	taladro.jpg	Taladro 20V con batería de litio y maletín	15	t	t	79990	2	2025-05-22 08:29:46.798962+00	2025-05-22 08:29:46.798962+00
10	Sierra Circular	129990	sierra.jpg	Sierra circular 1200W con guía láser	10	f	f	\N	2	2025-05-22 08:29:46.798962+00	2025-05-22 08:29:46.798962+00
11	Saco de Cemento	4990	cemento.jpg	Cemento tipo I, 25kg	100	f	f	\N	3	2025-05-22 08:29:46.798962+00	2025-05-22 08:29:46.798962+00
12	Ladrillos	29990	ladrillos.jpg	Ladrillos de arcilla, 100 unidades	50	f	f	\N	3	2025-05-22 08:29:46.798962+00	2025-05-22 08:29:46.798962+00
13	Pintura Interior	29990	pintura.jpg	Pintura látex interior 4L, color blanco	20	f	t	24990	4	2025-05-22 08:29:46.798962+00	2025-05-22 08:29:46.798962+00
14	Barniz Transparente	15990	barniz.jpg	Barniz poliuretánico 1L	25	f	f	\N	4	2025-05-22 08:29:46.798962+00	2025-05-22 08:29:46.798962+00
15	Set de Llaves	39990	llaves.jpg	Set de 8 llaves ajustables	15	f	f	\N	5	2025-05-22 08:29:46.798962+00	2025-05-22 08:29:46.798962+00
16	Tubería PVC	2990	tuberia.jpg	Tubería PVC 1/2" x 3m	100	f	f	\N	5	2025-05-22 08:29:46.798962+00	2025-05-22 08:29:46.798962+00
17	Cable Eléctrico	49990	cable.jpg	Cable 2.5mm² x 100m	30	f	f	\N	6	2025-05-22 08:29:46.798962+00	2025-05-22 08:29:46.798962+00
18	Interruptor Simple	3990	interruptor.jpg	Interruptor simple con placa	50	f	f	\N	6	2025-05-22 08:29:46.798962+00	2025-05-22 08:29:46.798962+00
19	Casco de Seguridad	15990	casco.jpg	Casco de seguridad industrial	40	t	f	\N	7	2025-05-22 08:29:46.798962+00	2025-05-22 08:29:46.798962+00
20	Guantes de Seguridad	8990	guantes.jpg	Guantes de cuero resistentes	60	f	f	\N	7	2025-05-22 08:29:46.798962+00	2025-05-22 08:29:46.798962+00
21	Cortadora de Césped	129990	cortadora.jpg	Cortadora de césped eléctrica 1200W	10	f	t	119990	8	2025-05-22 08:29:46.798962+00	2025-05-22 08:29:46.798962+00
22	Set de Jardinería	29990	jardin.jpg	Set de 5 herramientas de jardín	25	f	f	\N	8	2025-05-22 08:29:46.798962+00	2025-05-22 08:29:46.798962+00
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: ferremas
--

COPY public.users (id, username, password, email, created_at, updated_at, is_active, is_admin) FROM stdin;
1	xamppy	pbkdf2:sha256:1000000$Yz8gqqrKtQr1F6f4$11a2e9f3a401f1d6fa3eb58477c0805409212622991d2e8f881a2e9d3c5f0025	f.orellanalvarez@gmail.com	2025-05-22 08:38:19.324546+00	2025-05-22 08:38:19.324546+00	t	f
\.


--
-- Data for Name: webpay_transactions; Type: TABLE DATA; Schema: public; Owner: ferremas
--

COPY public.webpay_transactions (id, order_id, buy_order, token_ws, amount, status, transaction_date, authorization_code, payment_type_code, response_code, installments_number, card_number, transaction_detail, session_id, created_at, updated_at) FROM stdin;
1	1	OC-1	01ab5ff090e16e3aefa2e1ed920bc14ac9ee482704d54df2b4c736797199b67c	15990.00	initiated	\N	\N	\N	\N	\N	\N	\N	1	2025-05-22 08:40:09.385263+00	2025-05-22 08:40:10.066969+00
2	2	OC-2	01abf7d49cc92d0e2a705ed5ccb9f70562d367461dc6e6e77c25c031440896d0	89990.00	completed	\N	\N	\N	0	\N	\N	\N	1	2025-05-22 08:40:51.019511+00	2025-05-22 08:41:25.184482+00
\.


--
-- Name: cart_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ferremas
--

SELECT pg_catalog.setval('public.cart_items_id_seq', 4, true);


--
-- Name: categories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ferremas
--

SELECT pg_catalog.setval('public.categories_id_seq', 8, true);


--
-- Name: order_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ferremas
--

SELECT pg_catalog.setval('public.order_items_id_seq', 2, true);


--
-- Name: orders_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ferremas
--

SELECT pg_catalog.setval('public.orders_id_seq', 2, true);


--
-- Name: products_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ferremas
--

SELECT pg_catalog.setval('public.products_id_seq', 22, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ferremas
--

SELECT pg_catalog.setval('public.users_id_seq', 1, true);


--
-- Name: webpay_transactions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ferremas
--

SELECT pg_catalog.setval('public.webpay_transactions_id_seq', 2, true);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: ferremas
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: cart_items cart_items_pkey; Type: CONSTRAINT; Schema: public; Owner: ferremas
--

ALTER TABLE ONLY public.cart_items
    ADD CONSTRAINT cart_items_pkey PRIMARY KEY (id);


--
-- Name: categories categories_pkey; Type: CONSTRAINT; Schema: public; Owner: ferremas
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_pkey PRIMARY KEY (id);


--
-- Name: order_items order_items_pkey; Type: CONSTRAINT; Schema: public; Owner: ferremas
--

ALTER TABLE ONLY public.order_items
    ADD CONSTRAINT order_items_pkey PRIMARY KEY (id);


--
-- Name: orders orders_pkey; Type: CONSTRAINT; Schema: public; Owner: ferremas
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_pkey PRIMARY KEY (id);


--
-- Name: products products_pkey; Type: CONSTRAINT; Schema: public; Owner: ferremas
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_pkey PRIMARY KEY (id);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: ferremas
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: ferremas
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: ferremas
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: webpay_transactions webpay_transactions_buy_order_key; Type: CONSTRAINT; Schema: public; Owner: ferremas
--

ALTER TABLE ONLY public.webpay_transactions
    ADD CONSTRAINT webpay_transactions_buy_order_key UNIQUE (buy_order);


--
-- Name: webpay_transactions webpay_transactions_pkey; Type: CONSTRAINT; Schema: public; Owner: ferremas
--

ALTER TABLE ONLY public.webpay_transactions
    ADD CONSTRAINT webpay_transactions_pkey PRIMARY KEY (id);


--
-- Name: cart_items cart_items_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ferremas
--

ALTER TABLE ONLY public.cart_items
    ADD CONSTRAINT cart_items_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id);


--
-- Name: cart_items cart_items_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ferremas
--

ALTER TABLE ONLY public.cart_items
    ADD CONSTRAINT cart_items_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: order_items order_items_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ferremas
--

ALTER TABLE ONLY public.order_items
    ADD CONSTRAINT order_items_order_id_fkey FOREIGN KEY (order_id) REFERENCES public.orders(id) ON DELETE CASCADE;


--
-- Name: order_items order_items_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ferremas
--

ALTER TABLE ONLY public.order_items
    ADD CONSTRAINT order_items_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id) ON DELETE SET NULL;


--
-- Name: orders orders_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ferremas
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: products products_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ferremas
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.categories(id);


--
-- Name: webpay_transactions webpay_transactions_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ferremas
--

ALTER TABLE ONLY public.webpay_transactions
    ADD CONSTRAINT webpay_transactions_order_id_fkey FOREIGN KEY (order_id) REFERENCES public.orders(id) ON DELETE SET NULL;


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: ferremas
--

REVOKE USAGE ON SCHEMA public FROM PUBLIC;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--

