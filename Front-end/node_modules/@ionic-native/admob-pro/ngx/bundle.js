'use strict';

Object.defineProperty(exports, '__esModule', { value: true });

var tslib = require('tslib');
var core$1 = require('@angular/core');
var core = require('@ionic-native/core');
require('rxjs');

var AdMobPro = /** @class */ (function (_super) {
    tslib.__extends(AdMobPro, _super);
    function AdMobPro() {
        var _this = _super !== null && _super.apply(this, arguments) || this;
        _this.AD_POSITION = {
            NO_CHANGE: 0,
            TOP_LEFT: 1,
            TOP_CENTER: 2,
            TOP_RIGHT: 3,
            LEFT: 4,
            CENTER: 5,
            RIGHT: 6,
            BOTTOM_LEFT: 7,
            BOTTOM_CENTER: 8,
            BOTTOM_RIGHT: 9,
            POS_XY: 10,
        };
        return _this;
    }
    AdMobPro.prototype.createBanner = function (adIdOrOptions) { return core.cordova(this, "createBanner", {}, arguments); };
    AdMobPro.prototype.removeBanner = function () { return core.cordova(this, "removeBanner", { "sync": true }, arguments); };
    AdMobPro.prototype.showBanner = function (position) { return core.cordova(this, "showBanner", { "sync": true }, arguments); };
    AdMobPro.prototype.showBannerAtXY = function (x, y) { return core.cordova(this, "showBannerAtXY", { "sync": true }, arguments); };
    AdMobPro.prototype.hideBanner = function () { return core.cordova(this, "hideBanner", { "sync": true }, arguments); };
    AdMobPro.prototype.prepareInterstitial = function (adIdOrOptions) { return core.cordova(this, "prepareInterstitial", {}, arguments); };
    AdMobPro.prototype.showInterstitial = function () { return core.cordova(this, "showInterstitial", { "sync": true }, arguments); };
    AdMobPro.prototype.prepareRewardVideoAd = function (adIdOrOptions) { return core.cordova(this, "prepareRewardVideoAd", {}, arguments); };
    AdMobPro.prototype.showRewardVideoAd = function () { return core.cordova(this, "showRewardVideoAd", { "sync": true }, arguments); };
    AdMobPro.prototype.setOptions = function (options) { return core.cordova(this, "setOptions", {}, arguments); };
    AdMobPro.prototype.getAdSettings = function () { return core.cordova(this, "getAdSettings", {}, arguments); };
    AdMobPro.prototype.onAdFailLoad = function () { return core.cordova(this, "onAdFailLoad", { "eventObservable": true, "event": "onAdFailLoad", "element": "document" }, arguments); };
    AdMobPro.prototype.onAdLoaded = function () { return core.cordova(this, "onAdLoaded", { "eventObservable": true, "event": "onAdLoaded", "element": "document" }, arguments); };
    AdMobPro.prototype.onAdPresent = function () { return core.cordova(this, "onAdPresent", { "eventObservable": true, "event": "onAdPresent", "element": "document" }, arguments); };
    AdMobPro.prototype.onAdLeaveApp = function () { return core.cordova(this, "onAdLeaveApp", { "eventObservable": true, "event": "onAdLeaveApp", "element": "document" }, arguments); };
    AdMobPro.prototype.onAdDismiss = function () { return core.cordova(this, "onAdDismiss", { "eventObservable": true, "event": "onAdDismiss", "element": "document" }, arguments); };
    AdMobPro.pluginName = "AdMob Pro";
    AdMobPro.plugin = "cordova-plugin-admobpro";
    AdMobPro.pluginRef = "AdMob";
    AdMobPro.repo = "https://github.com/floatinghotpot/cordova-admob-pro";
    AdMobPro.platforms = ["Android", "iOS", "Windows Phone 8"];
    AdMobPro.decorators = [
        { type: core$1.Injectable }
    ];
    return AdMobPro;
}(core.IonicNativePlugin));

exports.AdMobPro = AdMobPro;
