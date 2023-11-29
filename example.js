p1.p2 = p3[p4]
p1.p2 = p3[p4.p5]
t = (t1) => {
  t2[t1] = 1
  t2[t1.t3] = 1
  t2[t4.t3] = 1
  t2[t4] = 1
}
// module.exports = (ctx) => {
//   ctx.idsArr = Object.keys(ctx.storesResponse);
//   ctx.stores = ctx.idsArr.filter((id) => {
//     ctx.hasRegionIds = parseInt(
//       ctx.getParsedInfo(ctx.storesResponse, id, 'regionIds')
//     );
//     ctx.hasRms =
//       ctx.getParsedInfo(ctx.storesResponse, id, 'rms_is_warehouse') == 1;
//     ctx.status = ctx.getParsedInfo(ctx.storesResponse, id, 'status');
//     ctx.hasCorrectStatus = ctx.status === 'new' || ctx.status === 'open';
//     ctx.isMarketplace =
//       ctx.getParsedInfo(ctx.storesResponse, id, 'isMarketplace') === 'true';
//     ctx.isRussianBU = ctx.getParsedInfo(ctx.storesResponse, id, 'num_bu') == 9;
//     return (
//       (ctx.hasRegionIds &&
//         ctx.hasRms &&
//         ctx.hasCorrectStatus &&
//         ctx.isRussianBU) ||
//       ctx.isMarketplace
//     );
//   });
//   return null;
// };

// module.exports = (ctx) => {
//   p1.p2.p3[ctx.familyParamName] = 1
// }
