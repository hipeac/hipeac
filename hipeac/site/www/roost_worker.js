"use strict";

var _roostSW = {
    version: 3,
    logging: true,
    appKey: "a253e21fb2404e8184943edd0bc67680",
    host: "https://go.goroost.com",
    pipeline: "https://pipeline.goroost.com"
};

self.addEventListener("install", function(evt) {
    //Automatically take over the previous worker.
    evt.waitUntil(self.skipWaiting());
});

self.addEventListener("activate", function(evt) {
    if (_roostSW.logging) console.log("Activated Roost ServiceWorker version: " + _roostSW.version);
});

//Handle the push received event.
self.addEventListener("push", function(evt) {
    if (_roostSW.logging) console.log("push listener", evt);
    evt.waitUntil(self.registration.pushManager.getSubscription().then(function(subscription) {
        var regID = null;
        var json = null;
        if ("subscriptionId" in subscription) {
            regID = subscription.subscriptionId;
        } else {
            //in Chrome 44+ and other SW browsers, reg ID is part of endpoint, send the whole thing and let the server figure it out.
            regID = subscription.endpoint;
        }
        if (evt.data !== null) {
            json = evt.data.json();
        }
        if (json && json.data) {
            if (_roostSW.logging) console.log("Showing notification: " + json.data.alert);
            var url = _roostSW.pipeline + "/push/redirect?noteID=" + json.data.roost_note_id + "&rdt=" + encodeURIComponent(regID);
            var title = json.data.title ? json.data.title : json.data.ar_app_name;
            var actions = json.data.actions ? json.data.actions : null;
            return showNotification(json.data.roost_note_id, title, json.data.alert, url, _roostSW.appKey, actions, regID, json.data.requireInteraction);
        } else {
            return fetch(_roostSW.host + "/api/browser/notifications?version=" + _roostSW.version + "&appKey=" + _roostSW.appKey + "&deviceID=" + encodeURIComponent(regID)).then(function(response) {
                return response.json().then(function(json) {
                    var promises = [];
                    for (var i = 0; i < json.notifications.length; i++) {
                        var note = json.notifications[i];
                        if (_roostSW.logging) console.log("Showing notification: " + note.body);
                        var url;
                        if (note.hasOwnProperty("roost_send_id")) {
                            url =  _roostSW.host + "/note/" + note.roost_note_id + "/" + note.roost_send_id + "?token=" + encodeURIComponent(regID);
                        } else {
                            url = _roostSW.pipeline + "/push/redirect?noteID=" + note.roost_note_id + "&rdt=" + encodeURIComponent(regID);
                        }
                        promises.push(showNotification(note.roost_note_id, note.title, note.body, url, _roostSW.appKey, note.actions, regID, note.requireInteraction));
                    }
                    return Promise.all(promises);
                });
            })
            .catch(function(e){
                var errorMessage = "Error in service worker: " + e.message;
                fetch(_roostSW.host + "/api/webhook/error/?appKey=" + _roostSW.appKey + "&deviceID=" + encodeURIComponent(regID) + "&errorMessage=" + encodeURIComponent(errorMessage));
            });
        }
    }));
});

self.addEventListener("notificationclick", function(evt) {
    if (_roostSW.logging) console.log("notificationclick listener", evt);
    evt.waitUntil(handleNotificationClick(evt));
});

function parseQueryString(queryString) {
    var qd = {};
    queryString.split("&").forEach(function (item) {
        var parts = item.split("=");
        var k = parts[0];
        var v = decodeURIComponent(parts[1]);
        (k in qd) ? qd[k].push(v) : qd[k] = [v, ]
    });
    return qd;
}

//Utility function to handle the click
function handleNotificationClick(evt) {
    if (_roostSW.logging) console.log("Notification clicked: ", evt.notification);
    evt.notification.close();
    var iconURL = evt.notification.icon;
    var url;
    var type;
    if (evt.action === "action_0") {
        type = evt.notification.data["action_0"].type;
        url = evt.notification.data["action_0"].url;
    } else if (evt.action === "action_1") {
        type = evt.notification.data["action_1"].type;
        url = evt.notification.data["action_1"].url;
    } else if (iconURL.indexOf("?") > -1) {
        var queryString = iconURL.split("?")[1];
        var query = parseQueryString(queryString);
        if (query.url && query.url.length == 1) {
            if (_roostSW.logging) console.log("Opening URL: " + query.url[0]);
            type = "redirect";
            url = query.url[0];
        }
    }
    if (type && type === "webhook") {
        return fetch(url);
    } else if (type && type === "redirect"){
        return clients.openWindow(url);
    }
    console.log("Failed to redirect to notification for iconURL: " + iconURL);
}

function showNotification(noteID, title, body, url, appKey, actions, regID, requireInteraction) {
    var parsedActions;
    var actionData = {};
    if (actions) {
        parsedActions = JSON.parse(actions);
        for (var i = 0; i < parsedActions.length; i++) {
            (function (parsedAction, idx) {
                var actionName = "action_" + idx;
                parsedAction.action = actionName;
                actionData[actionName] = {
                    url : parsedAction.url,
                    type : parsedAction.type
                };
                delete parsedAction.url;
                delete parsedAction.type;
            }(parsedActions[i], i));
        }
    }

    var options = {
        body: body,
        tag: "roost-" + noteID,
        icon: _roostSW.host + "/api/browser/logo?size=100&direct=true&appKey=" + _roostSW.appKey + "&noteID="+ noteID + "&url=" + encodeURIComponent(url)
    };

    if (parsedActions) {
        options.actions = parsedActions;
        options.data = actionData;
    }

    if (requireInteraction) {
        options.requireInteraction = true;
    }

    return self.registration.showNotification(title, options).then(function(){
        fetch(_roostSW.host + "/api/webhook/display/?appKey=" + _roostSW.appKey + "&noteID="+ noteID + "&deviceID=" + encodeURIComponent(regID));
    });
}