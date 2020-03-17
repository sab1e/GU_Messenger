Консольный мессенджер.

1. Описание модулей:
    а. common - пакет с утилитами приёма передачи данных и глобальными переменными, используемыми в проекте.
    б. logs - пакет с конфигурацией логирования и сами логи работы.
    в. unit_tests - автотесты для проверки работоспособности функций проекта
    г. client.py - основной клиентский модуль.
    д. decos.py - функция декоратор для логирования вызовов функций.
    е. errors.py - описание классов исключений, используемые в проекте.
    ё. launcher.py - вспомогательная утилита для одновременного запуска сервера и нескольких клиентов.
    ж. server.py - основной серверный модуль.

2. Клиентский модуль - client.py
    Модуль поддерживает отправку сообщений адресатам, одновременно с этим приём новых сообщений.
    Поддерживаются опции командной строки:
        а. Адрес сервера. Позволяет указать адрес сервера для подключения. По умолчанию Localhost.
        б. Порт сервера. Позволяет указать порт, по которому будет производиться подключение. По умолчанию 7777
        в. -n или --name. Имя пользователя в системе. По умолчанию не задан. Если не указать данный параметр, программа
            при запуске запросит имя пользователя для авторизации в системе.
    После запуска приложения будет произведена попытка установить соединение с сервером.
    В случае удачи будет выведена справка по внутренним командам приложения:
        а. message. Отправить сообщение. После ввода команды приложение запросит имя получателя и само сообщение.
        б. help. Повторно выводит справку о командах приложения.
        в. exit. Завершает работы приложения.

3. Серверный модуль - server.py
    Модуль обеспечивает пересылку сообщений поступаемых от клиентов адресатам. Сообщения обрабатываются на сервере
    и отправляются только адресату.
    Поддерживаются опции командной строки:
        a. Номер порта. Номер порта на котором сервер будет принимать входящие подключения. По умолчанию 7777
        б. Адрес. Адрес с которого сервер будет принимать подключения. По умолчанию слушаются все адреса.
    После запуска сервера никакие дополнительные действия не требуются.
