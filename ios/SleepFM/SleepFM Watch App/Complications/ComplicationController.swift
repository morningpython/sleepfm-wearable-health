//
//  ComplicationController.swift
//  SleepFM Watch App
//
//  Created by SleepFM Team on 2026/01/27.
//

import ClockKit
import SwiftUI

/// Complication 데이터 제공자
///
/// 워치페이스에 수면 점수를 표시합니다.
/// 
/// 지원 Complication Family:
/// - Circular Small: 원형 점수
/// - Rectangular: 점수 + 레이블
/// - Graphic Corner: 코너 게이지
/// - Graphic Circular: 원형 게이지
class ComplicationController: NSObject, CLKComplicationDataSource {
    // MARK: - Configuration
    
    /// 지원되는 Complication Family
    func getComplicationDescriptors(handler: @escaping ([CLKComplicationDescriptor]) -> Void) {
        let descriptor = CLKComplicationDescriptor(
            identifier: "SleepFMComplication",
            displayName: "SleepFM",
            supportedFamilies: [
                .circularSmall,
                .modularSmall,
                .modularLarge,
                .utilitarianSmall,
                .utilitarianSmallFlat,
                .utilitarianLarge,
                .graphicCorner,
                .graphicCircular,
                .graphicRectangular,
                .graphicExtraLarge
            ]
        )
        
        handler([descriptor])
    }
    
    // MARK: - Timeline Configuration
    
    /// 현재 타임라인 엔트리
    func getCurrentTimelineEntry(
        for complication: CLKComplication,
        withHandler handler: @escaping (CLKComplicationTimelineEntry?) -> Void
    ) {
        let sleepScore = getSleepScore()
        let template = createTemplate(for: complication.family, score: sleepScore)
        
        if let template = template {
            let entry = CLKComplicationTimelineEntry(date: Date(), complicationTemplate: template)
            handler(entry)
        } else {
            handler(nil)
        }
    }
    
    /// 타임라인 엔트리들
    func getTimelineEntries(
        for complication: CLKComplication,
        after date: Date,
        limit: Int,
        withHandler handler: @escaping ([CLKComplicationTimelineEntry]?) -> Void
    ) {
        // 수면 점수는 하루에 한번 업데이트되므로 추가 엔트리 없음
        handler(nil)
    }
    
    // MARK: - Placeholder
    
    func getLocalizableSampleTemplate(
        for complication: CLKComplication,
        withHandler handler: @escaping (CLKComplicationTemplate?) -> Void
    ) {
        handler(createTemplate(for: complication.family, score: 78))
    }
    
    // MARK: - Template Creation
    
    private func createTemplate(for family: CLKComplicationFamily, score: Int) -> CLKComplicationTemplate? {
        switch family {
        case .circularSmall:
            return createCircularSmallTemplate(score: score)
            
        case .modularSmall:
            return createModularSmallTemplate(score: score)
            
        case .modularLarge:
            return createModularLargeTemplate(score: score)
            
        case .utilitarianSmall, .utilitarianSmallFlat:
            return createUtilitarianSmallTemplate(score: score)
            
        case .utilitarianLarge:
            return createUtilitarianLargeTemplate(score: score)
            
        case .graphicCorner:
            return createGraphicCornerTemplate(score: score)
            
        case .graphicCircular:
            return createGraphicCircularTemplate(score: score)
            
        case .graphicRectangular:
            return createGraphicRectangularTemplate(score: score)
            
        case .graphicExtraLarge:
            return createGraphicExtraLargeTemplate(score: score)
            
        default:
            return nil
        }
    }
    
    // MARK: - Circular Small
    
    private func createCircularSmallTemplate(score: Int) -> CLKComplicationTemplate {
        let template = CLKComplicationTemplateCircularSmallStackText(
            line1TextProvider: CLKSimpleTextProvider(text: "😴"),
            line2TextProvider: CLKSimpleTextProvider(text: "\(score)")
        )
        return template
    }
    
    // MARK: - Modular Small
    
    private func createModularSmallTemplate(score: Int) -> CLKComplicationTemplate {
        let template = CLKComplicationTemplateModularSmallStackText(
            line1TextProvider: CLKSimpleTextProvider(text: "수면"),
            line2TextProvider: CLKSimpleTextProvider(text: "\(score)")
        )
        return template
    }
    
    // MARK: - Modular Large
    
    private func createModularLargeTemplate(score: Int) -> CLKComplicationTemplate {
        let template = CLKComplicationTemplateModularLargeStandardBody(
            headerTextProvider: CLKSimpleTextProvider(text: "SleepFM"),
            body1TextProvider: CLKSimpleTextProvider(text: "어젯밤 수면 점수"),
            body2TextProvider: CLKSimpleTextProvider(text: "\(score)점")
        )
        return template
    }
    
    // MARK: - Utilitarian Small
    
    private func createUtilitarianSmallTemplate(score: Int) -> CLKComplicationTemplate {
        let template = CLKComplicationTemplateUtilitarianSmallFlat(
            textProvider: CLKSimpleTextProvider(text: "수면 \(score)")
        )
        return template
    }
    
    // MARK: - Utilitarian Large
    
    private func createUtilitarianLargeTemplate(score: Int) -> CLKComplicationTemplate {
        let template = CLKComplicationTemplateUtilitarianLargeFlat(
            textProvider: CLKSimpleTextProvider(text: "수면 점수: \(score)점")
        )
        return template
    }
    
    // MARK: - Graphic Corner
    
    private func createGraphicCornerTemplate(score: Int) -> CLKComplicationTemplate {
        let gaugeProvider = CLKSimpleGaugeProvider(
            style: .fill,
            gaugeColor: scoreColor(for: score),
            fillFraction: Float(score) / 100.0
        )
        
        let template = CLKComplicationTemplateGraphicCornerGaugeText(
            gaugeProvider: gaugeProvider,
            outerTextProvider: CLKSimpleTextProvider(text: "\(score)")
        )
        return template
    }
    
    // MARK: - Graphic Circular
    
    private func createGraphicCircularTemplate(score: Int) -> CLKComplicationTemplate {
        let gaugeProvider = CLKSimpleGaugeProvider(
            style: .fill,
            gaugeColor: scoreColor(for: score),
            fillFraction: Float(score) / 100.0
        )
        
        let template = CLKComplicationTemplateGraphicCircularClosedGaugeText(
            gaugeProvider: gaugeProvider,
            centerTextProvider: CLKSimpleTextProvider(text: "\(score)")
        )
        return template
    }
    
    // MARK: - Graphic Rectangular
    
    private func createGraphicRectangularTemplate(score: Int) -> CLKComplicationTemplate {
        let template = CLKComplicationTemplateGraphicRectangularFullView(
            ComplicationRectangularView(score: score)
        )
        return template
    }
    
    // MARK: - Graphic Extra Large
    
    private func createGraphicExtraLargeTemplate(score: Int) -> CLKComplicationTemplate {
        let template = CLKComplicationTemplateGraphicExtraLargeCircularView(
            ComplicationExtraLargeView(score: score)
        )
        return template
    }
    
    // MARK: - Helpers
    
    private func getSleepScore() -> Int {
        // UserDefaults에서 마지막 수면 점수 가져오기
        let defaults = UserDefaults(suiteName: "group.com.sleepfm.shared")
        return defaults?.integer(forKey: "lastSleepScore") ?? 0
    }
    
    private func scoreColor(for score: Int) -> UIColor {
        switch score {
        case 80...100: return UIColor.green
        case 60..<80: return UIColor.blue
        case 40..<60: return UIColor.orange
        default: return UIColor.red
        }
    }
}

// MARK: - SwiftUI Complication Views

/// Rectangular Complication View
struct ComplicationRectangularView: View {
    let score: Int
    
    var body: some View {
        HStack {
            VStack(alignment: .leading, spacing: 2) {
                Text("어젯밤 수면")
                    .font(.caption2)
                    .foregroundColor(.secondary)
                
                HStack(alignment: .firstTextBaseline, spacing: 2) {
                    Text("\(score)")
                        .font(.system(size: 24, weight: .bold, design: .rounded))
                        .foregroundColor(scoreColor)
                    Text("점")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
            
            Spacer()
            
            Image(systemName: "moon.zzz.fill")
                .font(.title2)
                .foregroundColor(.purple)
        }
        .padding(.horizontal, 8)
    }
    
    private var scoreColor: Color {
        switch score {
        case 80...100: return .green
        case 60..<80: return .blue
        case 40..<60: return .orange
        default: return .red
        }
    }
}

/// Extra Large Circular Complication View
struct ComplicationExtraLargeView: View {
    let score: Int
    
    var body: some View {
        ZStack {
            Circle()
                .stroke(lineWidth: 8)
                .foregroundColor(.gray.opacity(0.3))
            
            Circle()
                .trim(from: 0, to: CGFloat(score) / 100)
                .stroke(
                    style: StrokeStyle(lineWidth: 8, lineCap: .round)
                )
                .foregroundColor(scoreColor)
                .rotationEffect(.degrees(-90))
            
            VStack(spacing: 2) {
                Text("\(score)")
                    .font(.system(size: 32, weight: .bold, design: .rounded))
                
                Text("수면 점수")
                    .font(.caption2)
                    .foregroundColor(.secondary)
            }
        }
        .padding(8)
    }
    
    private var scoreColor: Color {
        switch score {
        case 80...100: return .green
        case 60..<80: return .blue
        case 40..<60: return .orange
        default: return .red
        }
    }
}

// MARK: - Complication Update

extension ComplicationController {
    /// Complication 업데이트 요청
    static func reloadComplications() {
        let server = CLKComplicationServer.sharedInstance()
        
        for complication in server.activeComplications ?? [] {
            server.reloadTimeline(for: complication)
        }
    }
    
    /// 수면 점수 업데이트 및 Complication 새로고침
    static func updateSleepScore(_ score: Int) {
        let defaults = UserDefaults(suiteName: "group.com.sleepfm.shared")
        defaults?.set(score, forKey: "lastSleepScore")
        defaults?.set(Date().timeIntervalSince1970, forKey: "lastScoreUpdate")
        
        reloadComplications()
    }
}
